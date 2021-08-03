import os
import sys
from uuid import UUID
from itertools import starmap
from itertools import product

from gem5art.artifact import Artifact
from gem5art.run import gem5Run
from gem5art.tasks.tasks import run_gem5_instance
import multiprocessing as mp

packer = Artifact.registerArtifact(
    command = '''wget https://releases.hashicorp.com/packer/1.4.3/packer_1.4.3_linux_amd64.zip;
    unzip packer_1.4.3_linux_amd64.zip;
    ''',
    typ = 'binary',
    name = 'packer',
    path =  'disk-image/packer',
    cwd = 'disk-image',
    documentation = 'Program to build disk images. Downloaded sometime in August from hashicorp.'
)

experiments_repo = Artifact.registerArtifact(
    command = 'git clone https://https://gitee.com/liu-yanwei0503/parsec-tests.git',
    typ = 'git repo',
    name = 'parsec_tests',
    path =  './',
    cwd = '../',
    documentation = 'main repo to run parsec tests with gem5'
)

parsec_repo = Artifact.registerArtifact(
    command = '''mkdir parsec-benchmark/;
    cd parsec-benchmark;
    git clone ;''',
    typ = 'git repo',
    name = 'parsec_repo',
    path =  './disk-image/parsec/parsec-benchmark/',
    cwd = './disk-image/parsec',
    documentation = 'main repo to copy parsec source to the disk-image'
)

gem5_repo = Artifact.registerArtifact(
    command = 'git clone https://github.com/gem5/gem5.git',
    typ = 'git repo',
    name = 'gem5',
    path =  'gem5/',
    cwd = './',
    documentation = 'cloned gem5 from github and checked out release-staging-v21.0.0.0 (Mar 25, 2021)'
)

m5_binary = Artifact.registerArtifact(
    command = 'scons build/x86/out/m5',
    typ = 'binary',
    name = 'm5',
    path =  'gem5/util/m5/build/x86/out/m5',
    cwd = 'gem5/util/m5',
    inputs = [gem5_repo,],
    documentation = 'm5 utility'
)

disk_image = Artifact.registerArtifact(
    command = './packer build parsec/parsec.json',
    typ = 'disk image',
    name = 'parsec',
    cwd = 'disk-image',
    path = 'disk-image/parsec/parsec-image/parsec',
    inputs = [packer, experiments_repo, m5_binary, parsec_repo,],
    documentation = 'Ubuntu with m5 binary and PARSEC installed.'
)

gem5_binary = Artifact.registerArtifact(
    command = 'scons build/X86/gem5.opt -j160',
    typ = 'gem5 binary',
    name = 'gem5',
    cwd = 'gem5/',
    path =  'gem5/build/X86/gem5.opt',
    inputs = [gem5_repo,],
    documentation = 'gem5 binary'
)

gem5_binary_MESI_Three_Level = Artifact.registerArtifact(
    command = '''cd gem5;
    scons build/X86_MESI_Three_Level/gem5.opt --default=X86 PROTOCOL=MESI_Three_Level -j160
    ''',
    typ = 'gem5 binary',
    name = 'gem5',
    cwd = 'gem5/',
    path =  'gem5/build/X86_MESI_Three_Level/gem5.opt',
    inputs = [gem5_repo,],
    documentation = 'gem5 binary based on release-staging-v21.0.0.0 (Mar 25, 2021)'
)

gem5_binary_MESI_Two_Level = Artifact.registerArtifact(
    command = '''cd gem5;
    scons build/X86_MESI_Two_Level/gem5.opt --default=X86 PROTOCOL=MESI_Two_Level -j160
    ''',
    typ = 'gem5 binary',
    name = 'gem5',
    cwd = 'gem5/',
    path =  'gem5/build/X86_MESI_Two_Level/gem5.opt',
    inputs = [gem5_repo,],
    documentation = 'gem5 binary based on release-staging-v21.0.0.0 (Mar 25, 2021)'
)

linux_repo = Artifact.registerArtifact(
    command = '''git clone --branch v4.19.83 --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git;
    mv linux linux-stable''',
    typ = 'git repo',
    name = 'linux-stable',
    path =  'linux-stable/',
    cwd = './',
    documentation = 'linux kernel source code repo'
)

linux_binary = Artifact.registerArtifact(
    name = 'vmlinux-4.19.83',
    typ = 'kernel',
    path = 'linux-stable/vmlinux-4.19.83',
    cwd = 'linux-stable/',
    command = '''
    cp ../config.4.19.83 .config;
    make -j8;
    cp vmlinux vmlinux-4.19.83;
    ''',
    inputs = [experiments_repo, linux_repo,],
    documentation = "kernel binary for v4.19.83"
)


# if __name__ == "__main__":
#     num_cpus = ['1']
#     benchmarks = ['blackscholes']

#     sizes = ['simsmall']
#     cpus = ['timing']

#     for cpu in cpus:
#         for num_cpu in num_cpus:
#             for size in sizes:
#                 if cpu == 'timing' and size != 'simsmall':
#                     continue
#                 for bm in benchmarks:
#                     run = gem5Run.createFSRun(
#                         'parsec_tests',    
#                         'gem5/build/X86/gem5.opt',
#                         'configs/run_parsec.py',
#                         f'''results/run_parsec/{bm}/{size}/{cpu}/{num_cpu}''',
#                         gem5_binary, gem5_repo, experiments_repo,
#                         'linux-stable/vmlinux-4.19.83',
#                         'disk-image/parsec/parsec-image/parsec',
#                         linux_binary, disk_image,
#                         cpu, bm, size, num_cpu,
#                         timeout = 72*60*60 #24 hours
#                         )
#                     run_gem5_instance.apply_async((run, os.getcwd(), ))
linuxes = ['4.19.83']
def worker(run):
    run.run()
    json = run.dumpsJson()
    print(json)

# if __name__ == "__main__":
#     num_cpus = ['2']
#     benchmarks = ['blackscholes','bodytrack']
#     memory_system = ["MESI_Three_Level"]
#     # memory_system = ['classic']
#     sizes = ['simsmall','simlarge']
#     cpus = ['kvm']

#     def createRun(linux, cpus, memory_system, num_cpus, benchmarks, sizes):
#         return gem5Run.createFSRun(
#             'parsec_tests',    
#             'gem5/build/X86_MESI_Three_Level/gem5.opt',
#             'configs/run_parsec.py',
#             f'''results/run_parsec/{benchmarks}/{sizes}/{cpus}/{num_cpus}''',
#             gem5_binary, gem5_repo, experiments_repo,
#             'linux-stable/vmlinux-4.19.83',
#             'disk-image/parsec/parsec-image/parsec',
#             linux_binary, disk_image,
#             cpus, memory_system, benchmarks, sizes, num_cpus,
#             timeout = 96*60*60 #24 hours
#             )

#     jobs = []
#     # For the cross product of tests, create a run object.
#     runs = starmap(createRun, product(linuxes, cpus, memory_system, num_cpus, benchmarks, sizes))
#     # Run all of these experiments in parallel
#     for run in runs:
#         jobs.append(run)

#     with mp.Pool(mp.cpu_count() // 2) as pool:
#          pool.map(worker, jobs)

if __name__ == "__main__":
    num_cpus = ['128']
    benchmarks = ['blackscholes','bodytrack']
    memory_system = ["MESI_Two_Level"]
    # memory_system = ['classic']
    sizes = ['simsmall']
    cpus = ['timing']

    def createRun(linux, cpus, num_cpus, benchmarks, sizes):
        return gem5Run.createFSRun(
            'parsec_tests',    
            'gem5/build/X86_MESI_Two_Level/gem5.opt',
            'configs-mesi-two-level/run_parsec_mesi_two_level.py',
            f'''results/run_parsec/{benchmarks}/{sizes}/{cpus}/{num_cpus}''',
            gem5_binary_MESI_Two_Level, gem5_repo, experiments_repo,
            'linux-stable/vmlinux-4.19.83',
            'disk-image/parsec/parsec-image/parsec',
            linux_binary, disk_image,
            cpus, benchmarks, sizes, num_cpus,
            timeout = 96*60*60 #24 hours
            )

    jobs = []
    # For the cross product of tests, create a run object.
    runs = starmap(createRun, product(linuxes, cpus, num_cpus, benchmarks, sizes))
    # Run all of these experiments in parallel
    for run in runs:
        jobs.append(run)

    with mp.Pool(mp.cpu_count() // 2) as pool:
         pool.map(worker, jobs)
