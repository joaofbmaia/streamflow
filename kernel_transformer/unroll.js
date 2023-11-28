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

let totalUnrolledIterations = firstInnerLoop.descendantsAndSelf("loop")
    .map(x => (x.endValue - x.initValue) / x.stepValue)
    .reduce((x, y) => x * y, 1);

println(`Total unrolled iterations: ${totalUnrolledIterations}`);

// unroll inner loops
function unrollLoop(loop) {
    for (let i = parseInt(loop.initValue); i < parseInt(loop.endValue); i += parseInt(loop.stepValue)) {
        let bodyCopy = loop.body.copy();

        bodyCopy.descendants("varref")
            .filter(x => x.name == loop.controlVar)
            .map(x => x.replaceWith(`${i}`));

        loop.insertBefore(bodyCopy);
    }
    loop.detach();
}

innerLoopParent = firstInnerLoop.parent;

let i = innerLoopParent.descendants("loop")[0];
while (i !== undefined) {
    unrollLoop(i);
    i = innerLoopParent.descendants("loop")[0];
}

copyPragma = targetPragma.copy()
targetPragma.ancestor("body").insertBegin(copyPragma)
targetPragma.detach()

println("Unroll pass succeeded!");