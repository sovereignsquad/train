// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "TrainMacOS",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "Train", targets: ["Train"])
    ],
    targets: [
        .executableTarget(
            name: "Train",
            path: "Sources"
        )
    ]
)
