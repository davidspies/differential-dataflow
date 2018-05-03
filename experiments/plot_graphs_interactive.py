import shutil, tempfile
from executor import execute
from os import listdir
import sys

commit = sys.argv[sys.argv.index('--commit') + 1]
experiment = sys.argv[sys.argv.index('--experiment') + 1]

# commit = "dirty-e74441d0c062c7ec8d6da9bbf1972bd9397b2670"
# experiment = "arrange-open-loop"
print("commit {}, experiment {}".format(commit, experiment))


def eprint(*args):
    print(*args, file=sys.stderr)

def parsename(name):
    kvs = name.split('_')
    name, params = kvs[0], kvs[1:]
    def parsekv(kv):
        k, v = kv.split('=')
        if v.isdigit():
            v = int(v)
        return (k, v)
    return (name, sorted([parsekv(kv) for kv in params], key=lambda x: x[0]))

allfiles = [(parsename(f), f) for f in listdir("results/{}/{}".format(commit, experiment))]
allparams = list(zip(*allfiles))[0]
pivoted = list(zip(*list(zip(*allparams))[1]))
assert(all(all(y[0] == x[0][0] for y in x) for x in pivoted))
params = dict(list((x[0][0], set(list(zip(*x))[1])) for x in pivoted))
filedict = list((set(p[1]), f) for p, f in allfiles)
eprint(params)

def groupingstr(s):
    return '_'.join("{}={}".format(x[0], str(x[1])) for x in sorted(s, key=lambda x: x[0]))

def iii_memory_rss():
    tempdir = tempfile.mkdtemp("{}-{}".format(experiment, commit))

    filtering = set()
    for rate in params['rate']:
        F = filtering.union({ ('rate', rate), ('goal', 1800) })
        eprint(F)
        plotscript = "set terminal pdf size 6cm,4cm; set logscale y; " \
                "set bmargin at screen 0.2; " \
                "set xrange [-200:3500]; " \
                "set yrange [100000000:*]; " \
                "set xlabel \"minutes\"; " \
                "set ylabel \"RSS (bytes)\"; " \
                "set format y \"%.1s %c\"; " \
                "set key left top Left reverse font \",10\"; " \
                "set style fill  transparent solid 0.35 noborder; " \
                "set style circle radius 10; " \
                "plot "

        dt = 2
        for p, f in filedict:
            if p.issuperset(F):
                datafile = "{}/iii_memory_rss_{}".format(tempdir, f)
                assert(execute('cat results/{}/{}/{} | grep RSS | cut -f 2,3 > {}'.format(commit, experiment, f, datafile)))
                plotscript += "\"{}\" using ($1/1000000000):2 with circles title \"{}\", ".format(datafile, dict(p)['shared'])
                dt += 1

        assert(execute('mkdir -p plots/{}/{}'.format(commit, experiment)))
        eprint(plotscript)
        assert(execute('gnuplot > plots/{}/{}/iii_memory_rss_{}.pdf'.format(commit, experiment, groupingstr(F)), input=plotscript))
        eprint('plots/{}/{}/iii_memory_rss_{}.pdf'.format(commit, experiment, groupingstr(F)))

    shutil.rmtree(tempdir)


# def i_load_varies(): # commit = "dirty-8380c53277307b6e9e089a8f6f79886b36e20428" experiment = "arrange-open-loop"
#     tempdir = tempfile.mkdtemp("{}-{}".format(experiment, commit))
# 
#     filtering = { ('w', 1), }
#     for work in params['work']:
#         for comp in {'arrange', 'maintain', 'count'}:
#             F = filtering.union({ ('work', work), ('comp', comp), })
#             eprint(F)
#             # print('\n'.join(str(p) for p, f in sorted(filedict, key=lambda x: dict(x[0])['rate']) if p.issuperset(F)))
#             plotscript = "set terminal pdf size 6cm,4cm; set logscale x; set logscale y; " \
#                     "set bmargin at screen 0.2; " \
#                     "set xrange [50000:5000000000.0]; " \
#                     "set format x \"10^{%T}\"; " \
#                     "set yrange [0.005:1.01]; " \
#                     "set xlabel \"nanoseconds\"; " \
#                     "set format x \"10^{%T}\"; " \
#                     "set ylabel \"complementary cdf\"; " \
#                     "set key left bottom Left reverse font \",10\"; " \
#                     "plot "
#             dt = 2
#             for p, f in sorted(filedict, key=lambda x: dict(x[0])['rate']):
#                 if p.issuperset(F):
#                     datafile = "{}/i_load_varies_{}".format(tempdir, f)
#                     assert(execute('cat results/{}/{}/{} | grep LATENCYFRACTION | cut -f 3,4 > {}'.format(commit, experiment, f, datafile)))
#                     plotscript += "\"{}\" using 1:2 with lines lw 2 dt {} title \"{}\", ".format(datafile, dt, dict(p)['rate'])
#                     dt += 1
# 
#             assert(execute('mkdir -p plots/{}/{}'.format(commit, experiment)))
#             eprint(plotscript)
#             assert(execute('gnuplot > plots/{}/{}/i_load_varies_{}.pdf'.format(commit, experiment, groupingstr(F)), input=plotscript))
#             eprint('plots/{}/{}/i_load_varies_{}.pdf'.format(commit, experiment, groupingstr(F)))
# 
#     shutil.rmtree(tempdir)

