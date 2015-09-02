# coding: utf-8

import logging
import re
import time
import os
import subprocess
from tempfile import TemporaryFile

import settings

LOG = logging.getLogger(__name__)


def alive(prc):
    if not prc:
        return False
    return prc.poll() is None


def died_in(prc, timeout):
    start = time.time()
    while time.time() - start < timeout:
        if not alive(prc):
            return True
        time.sleep(0.01)
    return False


def kill_prc(prc, timeout=2):
    """
    kill subprocess prc
    """
    if not alive(prc):
        return
    prc.terminate()
    if died_in(prc, timeout):
        return
    LOG.error('can\'t terminate prc %s' % prc.pid)
    prc.kill()
    if died_in(prc, timeout):
        return
    LOG.error('can\'t kill prc %s' % prc.pid)
    os.kill(prc.pid, -9)


def run_process(cmd, timeout=10):
    """
    run process with timeout
    """
    if type(cmd) == bytes:
        cmd = cmd.decode('utf-8')
    if type(cmd) == str:
        cmd = cmd.split()
    if not timeout:
        subprocess.Popen(cmd)
        return None, None, None
    try:
        out = TemporaryFile()
        err = TemporaryFile()
        prc = subprocess.Popen(cmd, stdout=out, stderr=err)
    except:
        LOG.exception('error in run_process %s' % cmd)
        return -1, None, None
    starttime = time.time()
    while 1:
        if time.time() - starttime > timeout:
            LOG.error('run command %s timeout' % ' '.join(cmd))
            try:
                kill_prc(prc)
            except:
                pass
            return -1, None, None
        if not alive(prc):
            out.flush()
            err.flush()
            out.seek(0)
            err.seek(0)
            return prc.poll(), out.read().decode('utf-8'), err.read().decode('utf-8')
        time.sleep(0.1)


def run_command(cmd, timeout=30, lines=False):
    _, out, _ = run_process(cmd, timeout=timeout)
    if lines:
        return out.split('\n')
    else:
        return out


def send_command(cmd, addr, timeout=10):
    LOG.debug('%s %s %s' % (settings.heyu_binary, cmd, addr))
    try:
        return run_command('%s %s %s' % (settings.heyu_binary, cmd, addr), timeout)
    except Exception as e:
        LOG.exception('can\'t pass cmd "%s %s" to heyu: %s' % (cmd, addr, e))
        return None


def get_status(addr):
    s = send_command('status', addr, 5)
    if s:
        m = re.search('Status(\S+)', str(s))
        if m:
            return m.group(1).lower()
        else:
            LOG.error('no status in answer - %s' % s)
            return ''
    return ''


if __name__ == '__main__':
    print(send_command('status', 'a1'))
