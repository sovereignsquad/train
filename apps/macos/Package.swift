// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "train-macos",
    platforms: [
        .macOS(.v14)
    ],
    products: [
        .executable(name: "train", targets: ["train"])
    ],
    targets: [
        .executableTarget(
            name: "train",
            path: "Sources"
        )
    ]
)
