// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "AutotrainMacOS",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "Autotrain", targets: ["Autotrain"])
    ],
    targets: [
        .executableTarget(
            name: "Autotrain",
            path: "Sources"
        )
    ]
)
