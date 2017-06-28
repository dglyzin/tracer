from domainmodel.criminal.parser import Parser


def test_bounds():
    test_bounds_1d()
    test_bounds_2d()


def test_bounds_1d():
    parser = Parser()
    parser.params.blockNumber = 0
    parser.params.dim = '1D'
    parser.params.shape = [100]
    parser.parseMathExpression("-(U(t,{x, 0.7}))")
    print(parser.out)
    parser.parseMathExpression("-(U(t-1.1,{x, 0.7}))")
    print(parser.out)


def test_bounds_2d():
    parser = Parser()
    parser.params.blockNumber = 0
    parser.params.dim = '2D'
    parser.params.shape = [100, 1000]
    parser.parseMathExpression("-(U(t,{x, 0.7}{y, 0.3}))")
    print(parser.out)
    parser.parseMathExpression("-(U(t-1.1,{x, 0.7}{y, 0.3}))")
    print(parser.out)
