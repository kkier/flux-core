###############################################################
# Copyright 2019 Lawrence Livermore National Security, LLC
# (c.f. AUTHORS, NOTICE.LLNS, COPYING)
#
# This file is part of the Flux resource manager framework.
# For details, see https://github.com/flux-framework.
#
# SPDX-License-Identifier: LGPL-3.0
###############################################################

# Usage: flux python submit-sliding-window.py njobs fanout
#
# Run 'njobs' jobs, keeping at most 'fanout' active at once
#

import flux
from flux import job
import sys
import subprocess


# Return jobspec for a simple job
def make_jobspec(cmd):
    out = subprocess.Popen(
        ["flux", "jobspec", "srun", cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    stdout, stderr = out.communicate()
    return stdout


njobs = 10
fanout = 2
if len(sys.argv) >= 2:
    njobs = int(sys.argv[1])
if len(sys.argv) == 3:
    fanout = int(sys.argv[2])

# Open connection to broker
h = flux.Flux()

jobspec = make_jobspec("/bin/true")
flags = flux.constants.FLUX_JOB_WAITABLE
done = 0
running = 0

while done < njobs:
    if running < fanout and done + running < njobs:
        jobid = job.submit(h, jobspec, flags=flags)
        print("submit: {}".format(jobid))
        running += 1

    if running == fanout or done + running == njobs:
        jobid, success, errstr = job.wait(h)
        if success:
            print("wait: {} Success".format(jobid))
        else:
            print("wait: {} Error: {}".format(jobid, errstr))
        done += 1
        running -= 1

# vim: tabstop=4 shiftwidth=4 expandtab
