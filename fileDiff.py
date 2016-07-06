import sys
import filecmp

argc = len(sys.argv)

for i in range(1, argc - 1):
	for j in range(i + 1, argc):
		if filecmp.cmp(sys.argv[i], sys.argv[j], shallow=False):
			print "Test OK! " + sys.argv[i] + " " + sys.argv[j]
		else:
			print "TEST FAILED! " + sys.argv[i] + " " + sys.argv[j]