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

// add call to Morpher map function annotation
targetPragma.replaceWith("please_map_me();");

println("Morpher format pass succeeded!");