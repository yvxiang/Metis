#!/usr/bin/python

import subprocess, sys, os, multiprocessing

commonArgs = '-q'
sanityRun = True

passed = 0
failed = 0
skipped = 0

def execute(cmd, quiet = False):
    print '[%s]' % cmd
    f = open('/dev/null', 'w') if quiet else None
    p = subprocess.Popen(cmd, shell = True, stdout = f, stderr = f)
    p.communicate()
    if p.returncode != 0:
        print '\tFAIL'
        return False
    print '\tPASS'
    return True

def do_test(prog, args, sanityArgs = None, silent = False):
    global passed, failed, skipped
    cmd = ['./obj/%s' % prog]
    if sanityRun:
        if not sanityArgs:
            if not silent:
                print "skip %s: No sanity args provided" % prog
            skipped += 1
            return
        cmd.append(sanityArgs)
    else:
        cmd.append(args)
    cmd.append(commonArgs)
    if execute(' '.join(cmd)):
        passed += 1
    else:
        failed += 1

def test_path(path):
    if os.path.exists(path):
        return path
    return None

def test_all():
    do_test("wrmem", "", "-s 1")
    do_test("kmeans", "10 16 5000000 40", "10 16 5000 40")
    do_test("pca", "-R 2048 -C 2048", "-R %d -C 100" % (32 * multiprocessing.cpu_count()))
    do_test("matrix_mult", "-l 2048", "-l 100")
    do_test("hist", "data/hist-2.6g.bmp", test_path("data/3MB.bmp"))

    # The input is generated via data/data-gen.sh
    do_test("linear_regression", "data/lr_4GB.txt", test_path("data/lr_10MB.txt"))

    # The input is generated via data/data-gen.sh
    do_test("string_match", "data/sm_1GB.txt", test_path("data/wc/10MB.txt"))

    do_test("wc", "data/wc/300MB_1M_Keys.txt", test_path("data/wc/10MB.txt"))
    # this input is used for comparision with hadoop
    do_test("wc", "data/wc/10MB.txt -p 1", silent = True)

    # many keys and few duplicates
    do_test("wr", "data/wr/100MB_1M_Keys.txt", test_path("data/wc/10MB.txt"))
    # few keys and many duplicates
    do_test("wr", "data/wr/100MB_100K_Keys.txt", silent = True)
    # many keys and many duplicates. The input is generated via data/data-gen.sh
    do_test("wr", "data/wr/800MB.txt", silent = True)
    # many keys and many duplicates, but unpredictable. The input is generated by
    # data/data-gen.sh
    do_test("wr", "data/wr/500MB.txt", silent = True)

def rebuild_and_test(configure):
    execute("./configure %s" % configure, True)
    execute("make clean", True)
    ncore = multiprocessing.cpu_count()
    execute("make -j%d" % ncore, True)
    test_all()

rebuild_and_test("")
rebuild_and_test("--enable-mode=single_btree")
rebuild_and_test("--enable-mode=single_append-reduce_first")
rebuild_and_test("--enable-mode=single_append-group_merge_first")
rebuild_and_test("--enable-mode=single_append-nogroup_merge_first")
rebuild_and_test("--enable-sort=mergesort")
rebuild_and_test("--enable-mode=single_append-reduce_first --enable-sort=mergesort")
print "%d failed, %d passed, %d skipped" % (failed, passed, skipped)