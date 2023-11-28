laraImport("weaver.Query");

let pragmas = Query.search("pragma", { name: "cgra_map" }).get();
if (pragmas.length == 0) {
    throw new Error("\"#pragma cgra_map\" not found");
} else if (pragmas.length != 1) {
    throw new Error("Found more than one \"#pragma cgra_map\"");
}

let targetPragma = pragmas[0];

let firstInnerLoop = targetPragma.target;

if (firstInnerLoop.isOutermost) {
    throw new Error("\"#pragma cgra_map\" must be inside a for loop");
}

// generate an array with all the outer loops
let outerLoops = [];

let l = firstInnerLoop.ancestor("loop");
while (!l.isOutermost) {
    outerLoops.push(l);
    l = l.ancestor("loop");
}
outerLoops.push(l);


// generate index expressions
let controlVars = outerLoops.map((x) => x.controlVar);
let sizes = outerLoops.map((x) => x.endValue);
let steps = outerLoops.map((x) => x.stepValue);
let n = outerLoops.length;

// generated with AI assistance
function generateIndexExpressions(N, sizes, steps, dimNames) {
    let code = "";
    let dim = 0;
    for (dim = 0; dim < N; dim++) {
        let dimName = dimNames[dim];

        code += `int ${dimName} = (idx`;

        if (dim > 0) {
            code += " / (";
            for (let k = 0; k < dim; k++) {
                code += `${Math.floor(sizes[k] / steps[k])}`;
                if (k < dim - 1) code += " * ";
            }
            code += ")";
        }

        code += `) % ${Math.floor(sizes[dim] / steps[dim])} * ${steps[dim]};\n`;
    }
    return code;
}

// generated with AI assistance
function calculateMaxIdxRange(N, sizes, steps) {
    let totalIterations = 1;
    for (let dim = 0; dim < N; dim++) {
        totalIterations *= Math.ceil(sizes[dim] / steps[dim]);
    }
    return totalIterations;
}


let indexExpressions = generateIndexExpressions(n, sizes, steps, controlVars);
let maxRangeIdx = calculateMaxIdxRange(n, sizes, steps);

// setup new linearized outer loop
let linearOuterLoop = outerLoops[n - 1];

let innerBodyCopy = firstInnerLoop.parent.copy();
firstInnerLoop.detach();

linearOuterLoop.setBody(innerBodyCopy);
linearOuterLoop.body.insertBegin(indexExpressions);
linearOuterLoop.setInit("int idx = 0");
linearOuterLoop.setCond(`idx < ${maxRangeIdx}`);
linearOuterLoop.setStep("idx++");

// print stats
println(`Total trip count: ${maxRangeIdx}`);


println("Flatten pass succeeded!");