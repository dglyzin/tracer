
tests_list_main = [
    "U'=a*(D[U,{x,2}]+ D[U,{y,2}])",
    "a.t() = a",
    "(U)^3",
    "(V(t-1.1, {x, 0.7}{y, 0.7}))^3",
    "(D[V(t-1.1), {x, 2}])^3",
    '(U(t-1))^3',
    "D[U(t-1.1), {x,2}]+D[U(t-5.1), {y,2}]+D[V(t-1.1), {x,1}]",
    "-U(t,{x, a})",
    "(-U(t,{x, 0.7}{y, 0.7}))",
    "-V(t-1.1, {x, a}{y, 0.7})",
    "-(V+U)",
    "-U(t, {x, 0.7}{y, 0.3})",
    "(-U(t-1.1, {x, 0.7}{y, 0.3}))",
    "f(x, y)*t",
    
    "U'=a+U+U*U*V-(b+1)*U+c*D[U,{x,2}]",
    "U'=a+U*U*V-(b+1)*U+c*D[U,{x,2}]",
    "U",
    "U'=a+U*U*V-(b+1)*U+c*D[U,{x,2}]",
    "U'=a+U*U*V-(b+1)*U+c*(D[U,{x,2}]+D[U,{y,2}])",
    "U'=a+U*U*V-(b+1)*U+c*(D[U,{x,2}]+D[U,{y,2}])",
    "U'= a * D[U,{x,2}]",
    "U'= a * (D[U,{x,2}] + D[U,{y,2}])",
    "U'= a * (D[U,{x,2}] + D[U,{y,2}])",
    
    "U'= a * (D[U,{x,2}] + D[U,{y,2}])",
    "U'= a * (D[U,{x,2}] + D[U,{y,2}])",
    "U'= 0",
    "U'= b * (D[U,{x,2}] + D[U,{y,2}])",
    "U'= a * (D[U,{x,2}] + D[U,{y,2}])",
    "U'=a*(D[U,{x,2}] + D[U,{y,2}])",
    "U'=a*(D[U,{x,2}] + D[U,{y,2}])",
    "U'=a*(D[U,{x,2}] + D[U,{y,2}])",
    "U'= D[U,{x,2}]",
    "U'=a*D[U,{x,2}]+ r*U*(1-U(t-1))",
    "U'=a*D[U,{x,2}]+ r*U*(1-U(t-1))",
    "U'= D[U,{x,2}] + D[V,{x,2}]",
    "U'=a*D[U,{x,2}] + d*U",
    "U(t,{x,0.7}{y, 0.7})",
    "U'=a*D[U,{x,2}]",
    "U'=a*(D[U,{x,2}] + D[U,{y,2}])",
    "U'=a*(D[U,{x,2}]+D[U,{y,2}])+U(t-3.1)+U(t-1.3)",
    "U'= D[U,{x,2}]",
    "U'=2.0 - V",
    "(U(t-1.3,{x, 0.7}{y,0.3}))",
    "U'=a*(D[U,{x,2}] + D[U,{y,2}])",
    "U",
    "U'=a * (D[U,{x,2}] + D[U,{y,2}])",
    "U'=b * (D[U,{x,2}] + D[U,{y,2}])",
    "U'=a+U*U*V-(b+1)*U+c*(D[U,{x,2}]+D[U,{y,2}])",
    "U'=a * (D[U,{x,2}] + D[U,{y,2}])",
    "U'=2.0 - V",
    "U'=a*(D[U,{x,2}] + D[U,{y,2}])",
    "U'=a*(sin(a+b)+(U)^3)",
    ("(V(t-3.1)*U(t-3.1)+V(t-1.1)*U(t-3.1)+U(t-1.1))^3"
     + "+cos(U-c*D[U,{x,2}])"),
    ("U'=(V(t-3.1)*U(t-3.1)+V(t-1.1)*U(t-3.1)+U(t-1.1))^3"
     + "+cos(U-c*D[U,{x,2}])"),
    "U'=U",
    "U'=-U",
    "U'=-(U+V)",
    "U",
    "-(U(t-1.1)+V)",
    "U'=-(U(t-1.1)+V)",
    "f(x, y,)+g(y,z,)+h(x,z,)",
    "exp(t)"]

