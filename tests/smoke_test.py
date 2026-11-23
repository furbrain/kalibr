#!/usr/bin/env python3
"""End-to-end smoke test for the ROS-independent Kalibr build.

Renders a synthetic AprilGrid sequence seen by a pinhole-radtan camera with
known intrinsics, writes it to a ROS 2 bag with kalibr_bagcreater, runs
kalibr_calibrate_cameras on it and checks that the intrinsics are recovered.

With --imu it instead simulates a smooth camera trajectory with a rigidly
attached IMU and checks that kalibr_calibrate_imu_camera recovers the
camera-IMU transformation.

Usage: tests/smoke_test.py [--keep] [--bag-format ros2|mcap|ros1] [--imu]
The kalibr_* tools must be on PATH (or set KALIBR_BIN_DIR).
"""
import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile

import cv2
import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET_PDF_SCRIPT = os.path.join(HERE, '..', 'aslam_offline_calibration', 'kalibr', 'python',
                                 'kalibr_create_target_pdf')

# Ground truth camera (pinhole-radtan)
WIDTH, HEIGHT = 752, 480
K_TRUE = [458.0, 457.0, 367.0, 248.0]      # fu fv pu pv
D_TRUE = [-0.25, 0.06, 0.0002, -0.0001]    # k1 k2 r1 r2

# AprilGrid
NX, NY, TAG_SIZE, TAG_SPACING = 6, 6, 0.088, 0.3
PX_PER_M = 3000.0


def tag36h11Codes():
    """Reads the tag codes from kalibr_create_target_pdf (single source of truth)."""
    with open(TARGET_PDF_SCRIPT) as f:
        for line in f:
            if line.strip().startswith('t36h11='):
                return eval(line.split('=', 1)[1])
    raise RuntimeError("tag codes not found")


def renderAprilGrid():
    """Texture of the board; returns (image, board->texture affine)."""
    codes = tag36h11Codes()
    bits, border = 6, 2
    margin = 2 * TAG_SPACING * TAG_SIZE
    extent_x = NX * TAG_SIZE + (NX - 1) * TAG_SPACING * TAG_SIZE
    extent_y = NY * TAG_SIZE + (NY - 1) * TAG_SPACING * TAG_SIZE
    w = int(math.ceil((extent_x + 2 * margin) * PX_PER_M))
    h = int(math.ceil((extent_y + 2 * margin) * PX_PER_M))
    img = np.full((h, w), 255, np.uint8)

    def fill(x, y, sx, sy):  # board coords [m], y up, (x,y) = lower left corner
        c0 = int(round((x + margin) * PX_PER_M))
        c1 = int(round((x + sx + margin) * PX_PER_M))
        r0 = int(round(h - (y + sy + margin) * PX_PER_M))
        r1 = int(round(h - (y + margin) * PX_PER_M))
        img[r0:r1, c0:c1] = 0

    bit = TAG_SIZE / (bits + 2 * border)
    sq = TAG_SPACING * TAG_SIZE
    for ty in range(NY):
        for tx in range(NX):
            tag_id = NX * ty + tx
            x0 = tx * (1 + TAG_SPACING) * TAG_SIZE
            y0 = ty * (1 + TAG_SPACING) * TAG_SIZE
            b = border * bit
            fill(x0, y0, TAG_SIZE, b)
            fill(x0, y0 + TAG_SIZE - b, TAG_SIZE, b)
            fill(x0 + TAG_SIZE - b, y0, b, TAG_SIZE)
            fill(x0, y0, b, TAG_SIZE)
            code = np.zeros((bits, bits))
            for i in range(bits):
                for j in range(bits):
                    if not codes[tag_id] & (1 << bits * i + j):
                        code[i, j] = 1
            code = np.rot90(code, 2)
            for i in range(bits):
                for j in range(bits):
                    if code[i, j]:
                        fill(x0 + (j + border) * bit, y0 + ((border - 1) + bits - i) * bit, bit, bit)
            for cx, cy in [(x0 - sq, y0 - sq), (x0 + TAG_SIZE, y0 - sq),
                           (x0 + TAG_SIZE, y0 + TAG_SIZE), (x0 - sq, y0 + TAG_SIZE)]:
                fill(cx, cy, sq, sq)
    img = cv2.GaussianBlur(img, (0, 0), 0.7)
    # board (x, y) [m] -> texture (col, row)
    A = np.array([[PX_PER_M, 0, margin * PX_PER_M],
                  [0, -PX_PER_M, h - margin * PX_PER_M],
                  [0, 0, 1]])
    return img, A, (extent_x, extent_y)


def rotation(rx, ry, rz):
    R, _ = cv2.Rodrigues(np.array([rx, ry, rz], dtype=np.float64))
    return R


def renderView(texture, A, R, t):
    """Image of the board (plane z=0, pose R,t: board -> camera)."""
    K = np.array([[K_TRUE[0], 0, K_TRUE[2]], [0, K_TRUE[1], K_TRUE[3]], [0, 0, 1]])
    D = np.array(D_TRUE)
    us, vs = np.meshgrid(np.arange(WIDTH, dtype=np.float64), np.arange(HEIGHT, dtype=np.float64))
    pix = np.stack([us.ravel(), vs.ravel()], axis=1).reshape(-1, 1, 2)
    und = cv2.undistortPointsIter(pix, K, D, None, None,
                                  (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 40, 1e-10)).reshape(-1, 2)
    rays = np.hstack([und, np.ones((und.shape[0], 1))])
    H = np.column_stack([R[:, 0], R[:, 1], t])  # rays ~ H [x y 1]
    board = np.linalg.solve(H, rays.T).T
    valid = board[:, 2] > 0
    board = board[:, :2] / board[:, 2:3]
    tex = (A @ np.hstack([board, np.ones((board.shape[0], 1))]).T).T
    mapx = np.where(valid, tex[:, 0], -1).reshape(HEIGHT, WIDTH).astype(np.float32)
    mapy = np.where(valid, tex[:, 1], -1).reshape(HEIGHT, WIDTH).astype(np.float32)
    img = cv2.remap(texture, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=200)
    rng = np.random.default_rng(int(abs(t[0]) * 1e6) % 1000)
    return np.clip(img + rng.normal(0, 1.5, img.shape), 0, 255).astype(np.uint8)


def poses(extent, n=40):
    rng = np.random.default_rng(42)
    center = np.array([extent[0] / 2, extent[1] / 2, 0.0])
    out = []
    for i in range(n):
        # camera looks at the board from ~0.6-0.9 m; board tilted by up to ~35 deg
        R = rotation(math.pi + rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), rng.uniform(-0.4, 0.4))
        dist = rng.uniform(0.6, 0.9)
        offset = np.array([rng.uniform(-0.12, 0.12), rng.uniform(-0.08, 0.08), dist])
        t = offset - R @ center
        out.append((R, t))
    return out


#############################################################################
# Camera-IMU simulation
#############################################################################
# IMU -> camera (p_cam = R_CI p_imu + T_CI)
R_CI = None  # set in main (needs cv2)
T_CI = np.array([0.04, -0.015, 0.025])
GRAVITY_B = np.array([0.0, -9.81, 0.0])  # board mounted vertically
IMU_RATE, CAM_RATE, DURATION = 200.0, 20.0, 20.0
ACC_NOISE, GYR_NOISE = 0.002, 0.0002  # continuous time noise densities


def cameraPose(t, extent):
    """Board -> camera rotation and camera centre in board coordinates at time t."""
    R_cb = rotation(math.pi + 0.45 * math.sin(0.9 * t) + 0.1 * math.sin(2.3 * t),
                    0.45 * math.sin(0.7 * t + 1.0) + 0.1 * math.sin(1.9 * t),
                    0.35 * math.sin(0.5 * t + 2.0))
    offset = np.array([0.06 * math.sin(1.1 * t), 0.05 * math.sin(1.3 * t + 0.5),
                       0.75 + 0.12 * math.sin(0.6 * t)])  # board centre in camera coords
    center = np.array([extent[0] / 2, extent[1] / 2, 0.0])
    c_b = center - R_cb.T @ offset
    return R_cb, c_b


def imuPose(t, extent):
    R_cb, c_b = cameraPose(t, extent)
    R_bc = R_cb.T
    return R_bc @ R_CI, c_b + R_bc @ T_CI


def imuMeasurements(extent, rng):
    h = 1e-3
    rows = []
    for k in range(int(DURATION * IMU_RATE) + 1):
        t = k / IMU_RATE
        R_m, p_m = imuPose(t - h, extent)
        R_0, p_0 = imuPose(t, extent)
        R_p, p_p = imuPose(t + h, extent)
        acc_b = (p_p - 2 * p_0 + p_m) / (h * h)
        omega, _ = cv2.Rodrigues(R_m.T @ R_p)
        omega = omega.ravel() / (2 * h)
        accel = R_0.T @ (acc_b - GRAVITY_B)
        omega += rng.normal(0, GYR_NOISE * math.sqrt(IMU_RATE), 3)
        accel += rng.normal(0, ACC_NOISE * math.sqrt(IMU_RATE), 3)
        rows.append((t, omega, accel))
    return rows


def runImuTest(work, bag_format):
    global R_CI
    R_CI = rotation(0.03, -0.05, 0.02)
    rng = np.random.default_rng(7)
    texture, A, extent = renderAprilGrid()
    t0 = 1600000000 * 10**9
    os.makedirs(os.path.join(work, 'data', 'cam0'))
    for k in range(int(DURATION * CAM_RATE)):
        t = k / CAM_RATE
        R_cb, c_b = cameraPose(t, extent)
        img = renderView(texture, A, R_cb, -R_cb @ c_b)
        cv2.imwrite(os.path.join(work, 'data', 'cam0', '{0}.png'.format(t0 + int(round(t * 1e9)))), img)
    with open(os.path.join(work, 'data', 'imu0.csv'), 'w') as f:
        f.write('timestamp,omega_x,omega_y,omega_z,alpha_x,alpha_y,alpha_z\n')
        for t, w, a in imuMeasurements(extent, rng):
            f.write('{0},{1},{2},{3},{4},{5},{6}\n'.format(t0 + int(round(t * 1e9)), *w, *a))

    bag = makeBag(work, bag_format)
    writeTarget(work)
    with open(os.path.join(work, 'camchain.yaml'), 'w') as f:
        yaml.safe_dump({'cam0': {'camera_model': 'pinhole', 'intrinsics': K_TRUE,
                                 'distortion_model': 'radtan', 'distortion_coeffs': D_TRUE,
                                 'resolution': [WIDTH, HEIGHT], 'rostopic': '/cam0/image_raw'}}, f)
    with open(os.path.join(work, 'imu.yaml'), 'w') as f:
        yaml.safe_dump({'rostopic': '/imu0', 'update_rate': IMU_RATE,
                        'accelerometer_noise_density': ACC_NOISE, 'accelerometer_random_walk': 3e-5,
                        'gyroscope_noise_density': GYR_NOISE, 'gyroscope_random_walk': 2e-6}, f)

    env = dict(os.environ, MPLBACKEND='Agg')
    subprocess.check_call(tool('kalibr_calibrate_imu_camera') + [
        '--bag', bag, '--cam', 'camchain.yaml', '--imu', 'imu.yaml', '--target', 'april.yaml',
        '--dont-show-report'], cwd=work, env=env)

    tag = os.path.splitext(os.path.normpath(bag))[0]
    with open(os.path.join(work, tag + '-camchain-imucam.yaml')) as f:
        cam = yaml.safe_load(f)['cam0']
    T = np.array(cam['T_cam_imu'])
    rot_err = np.degrees(np.linalg.norm(cv2.Rodrigues(T[:3, :3].T @ R_CI)[0]))
    trans_err = np.linalg.norm(T[:3, 3] - T_CI)
    print("\nT_cam_imu translation true {0}\n                      est  {1}".format(
        T_CI.tolist(), np.round(T[:3, 3], 4).tolist()))
    print("rotation error {0:.3f} deg, translation error {1:.4f} m, time shift {2:.5f} s".format(
        rot_err, trans_err, cam['timeshift_cam_imu']))
    if rot_err > 0.5 or trans_err > 0.01 or abs(cam['timeshift_cam_imu']) > 0.002:
        print("FAILED: camera-IMU calibration does not match the ground truth")
        return 1
    print("PASSED")
    return 0


def makeBag(work, bag_format):
    bag = {'ros2': 'calib_bag', 'mcap': 'calib_bag', 'ros1': 'calib.bag'}[bag_format]
    cmd = tool('kalibr_bagcreater') + ['--folder', 'data', '--output-bag', bag]
    if bag_format == 'mcap':
        cmd += ['--storage', 'mcap']
    subprocess.check_call(cmd, cwd=work)
    return bag


def writeTarget(work):
    with open(os.path.join(work, 'april.yaml'), 'w') as f:
        yaml.safe_dump({'target_type': 'aprilgrid', 'tagCols': NX, 'tagRows': NY,
                        'tagSize': TAG_SIZE, 'tagSpacing': TAG_SPACING}, f)


def tool(name):
    bindir = os.environ.get('KALIBR_BIN_DIR')
    path = os.path.join(bindir, name) if bindir else shutil.which(name)
    if not path:
        raise RuntimeError("{0} not found on PATH".format(name))
    return [sys.executable, path]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--keep', action='store_true', help='keep the temporary directory')
    parser.add_argument('--bag-format', choices=['ros2', 'mcap', 'ros1'], default='ros2')
    parser.add_argument('--imu', action='store_true', help='run the camera-IMU calibration test')
    args = parser.parse_args()

    work = tempfile.mkdtemp(prefix='kalibr_smoke_')
    print("Working directory:", work)
    try:
        if args.imu:
            return runImuTest(work, args.bag_format)
        texture, A, extent = renderAprilGrid()
        os.makedirs(os.path.join(work, 'data', 'cam0'))
        t0 = 1600000000 * 10**9
        for i, (R, t) in enumerate(poses(extent)):
            cv2.imwrite(os.path.join(work, 'data', 'cam0', '{0}.png'.format(t0 + i * 200000000)),
                        renderView(texture, A, R, t))
        bag = makeBag(work, args.bag_format)
        writeTarget(work)

        env = dict(os.environ, MPLBACKEND='Agg')
        subprocess.check_call(tool('kalibr_calibrate_cameras') + [
            '--bag', bag, '--topics', '/cam0/image_raw', '--models', 'pinhole-radtan',
            '--target', 'april.yaml', '--dont-show-report'], cwd=work, env=env)

        tag = os.path.splitext(os.path.normpath(bag))[0]
        with open(os.path.join(work, tag + '-camchain.yaml')) as f:
            cam = yaml.safe_load(f)['cam0']
        k, d = cam['intrinsics'], cam['distortion_coeffs']
        print("\nintrinsics  true {0}\n            est  {1}".format(K_TRUE, np.round(k, 3).tolist()))
        print("distortion  true {0}\n            est  {1}".format(D_TRUE, np.round(d, 5).tolist()))
        assert cam['resolution'] == [WIDTH, HEIGHT], cam['resolution']
        assert cam['rostopic'] == '/cam0/image_raw'
        k_err = np.abs(np.array(k) - K_TRUE)
        d_err = np.abs(np.array(d[:2]) - D_TRUE[:2])
        if np.any(k_err > 2.0) or np.any(d_err > 0.01):
            print("FAILED: calibration does not match the ground truth")
            return 1
        print("PASSED")
        return 0
    finally:
        if args.keep:
            print("Kept", work)
        else:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
