import AppKit
import Foundation

let outputPath = CommandLine.arguments.dropFirst().first

guard let outputPath else {
    fputs("usage: swift generate_app_icon.swift /path/to/output.png\n", stderr)
    exit(1)
}

let size = CGSize(width: 1024, height: 1024)
let image = NSImage(size: size)

image.lockFocus()

guard let context = NSGraphicsContext.current?.cgContext else {
    fputs("failed to acquire graphics context\n", stderr)
    exit(1)
}

let bounds = CGRect(origin: .zero, size: size)
let backgroundPath = NSBezierPath(
    roundedRect: bounds.insetBy(dx: 36, dy: 36),
    xRadius: 220,
    yRadius: 220
)
backgroundPath.addClip()

let colorSpace = CGColorSpaceCreateDeviceRGB()
let gradientColors = [
    NSColor(calibratedRed: 0.04, green: 0.07, blue: 0.12, alpha: 1.0).cgColor,
    NSColor(calibratedRed: 0.07, green: 0.22, blue: 0.32, alpha: 1.0).cgColor,
    NSColor(calibratedRed: 0.95, green: 0.55, blue: 0.18, alpha: 1.0).cgColor,
] as CFArray

let locations: [CGFloat] = [0.0, 0.56, 1.0]
let gradient = CGGradient(colorsSpace: colorSpace, colors: gradientColors, locations: locations)!
context.drawLinearGradient(
    gradient,
    start: CGPoint(x: 120, y: 120),
    end: CGPoint(x: 924, y: 924),
    options: []
)

context.saveGState()
context.setShadow(offset: CGSize(width: 0, height: -28), blur: 48, color: NSColor.black.withAlphaComponent(0.24).cgColor)
let coreRect = CGRect(x: 238, y: 238, width: 548, height: 548)
let corePath = NSBezierPath(roundedRect: coreRect, xRadius: 160, yRadius: 160)
NSColor(calibratedRed: 0.04, green: 0.09, blue: 0.12, alpha: 0.90).setFill()
corePath.fill()
context.restoreGState()

context.setLineWidth(30)
NSColor.white.withAlphaComponent(0.18).setStroke()
let outerRing = NSBezierPath(ovalIn: CGRect(x: 150, y: 150, width: 724, height: 724))
outerRing.stroke()

context.setLineWidth(16)
NSColor.white.withAlphaComponent(0.10).setStroke()
let innerRing = NSBezierPath(ovalIn: CGRect(x: 214, y: 214, width: 596, height: 596))
innerRing.stroke()

let nodeFill = NSColor(calibratedRed: 0.95, green: 0.61, blue: 0.22, alpha: 1.0)
for point in [
    CGPoint(x: 512, y: 882),
    CGPoint(x: 858, y: 512),
    CGPoint(x: 512, y: 142),
    CGPoint(x: 166, y: 512),
] {
    let nodePath = NSBezierPath(ovalIn: CGRect(x: point.x - 28, y: point.y - 28, width: 56, height: 56))
    nodeFill.setFill()
    nodePath.fill()
}

context.saveGState()
context.setShadow(
    offset: CGSize(width: 0, height: -22),
    blur: 44,
    color: NSColor.black.withAlphaComponent(0.28).cgColor
)

let verticalStem = NSBezierPath(
    roundedRect: CGRect(x: 438, y: 264, width: 148, height: 476),
    xRadius: 74,
    yRadius: 74
)
NSColor.white.setFill()
verticalStem.fill()

let topBar = NSBezierPath(
    roundedRect: CGRect(x: 292, y: 646, width: 440, height: 118),
    xRadius: 59,
    yRadius: 59
)
topBar.fill()
context.restoreGState()

let insetGlow = NSBezierPath(
    roundedRect: CGRect(x: 326, y: 616, width: 372, height: 58),
    xRadius: 29,
    yRadius: 29
)
NSColor(calibratedRed: 0.98, green: 0.66, blue: 0.26, alpha: 0.92).setFill()
insetGlow.fill()

image.unlockFocus()

guard let tiff = image.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: tiff),
      let png = bitmap.representation(using: .png, properties: [:]) else {
    fputs("failed to create PNG representation\n", stderr)
    exit(1)
}

let outputURL = URL(fileURLWithPath: outputPath)
try FileManager.default.createDirectory(at: outputURL.deletingLastPathComponent(), withIntermediateDirectories: true)
try png.write(to: outputURL)
