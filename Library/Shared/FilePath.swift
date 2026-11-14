import Foundation

public enum FilePath {
    public static let packageName = AppConfiguration.packageName
    public static let groupName = AppConfiguration.appGroupID

    private static let defaultSharedDirectory: URL! = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: groupName)

    /// Check this before constructing services that use sharedDirectory. Missing
    /// signing authorization is a startup error, not a reason to use private storage.
    public static func requireSharedDirectory() throws -> URL {
        guard let directory = defaultSharedDirectory else {
            throw NSError(domain: "SharedContainer", code: 1, userInfo: [
                NSLocalizedDescriptionKey: String(localized: "Cannot access shared App Group: \(groupName). Re-sign the app and Packet Tunnel with separate matching profiles that authorize this group."),
            ])
        }
        return directory
    }

    #if os(iOS)
        public static let sharedDirectory = defaultSharedDirectory!
    #elseif os(tvOS)
        public static let sharedDirectory = defaultSharedDirectory
            .appendingPathComponent("Library", isDirectory: true)
            .appendingPathComponent("Caches", isDirectory: true)
    #elseif os(macOS)
        public static var sharedDirectory: URL! = defaultSharedDirectory
    #endif

    #if os(iOS)
        public static let cacheDirectory = sharedDirectory
            .appendingPathComponent("Library", isDirectory: true)
            .appendingPathComponent("Caches", isDirectory: true)
    #elseif os(tvOS)
        public static let cacheDirectory = sharedDirectory
    #elseif os(macOS)
        public static var cacheDirectory: URL {
            sharedDirectory
                .appendingPathComponent("Library", isDirectory: true)
                .appendingPathComponent("Caches", isDirectory: true)
        }
    #endif

    #if os(macOS)
        public static var workingDirectory: URL {
            cacheDirectory.appendingPathComponent("Working", isDirectory: true)
        }
    #else
        public static let workingDirectory = cacheDirectory.appendingPathComponent("Working", isDirectory: true)

    #endif

    public static func requireICloudDirectory() throws -> URL {
        guard !Variant.nativeVPNOnly else {
            throw NSError(domain: "NativeVPN", code: 1, userInfo: [NSLocalizedDescriptionKey: String(localized: "iCloud profiles are unavailable in the native VPN build. Import the file as a Local profile.")])
        }
        return iCloudDirectory
    }

    public static var iCloudDirectory = FileManager.default.url(forUbiquityContainerIdentifier: nil)?.appendingPathComponent("Documents", isDirectory: true) ?? URL(string: "stub")!
}

public extension URL {
    var fileName: String {
        var path = relativePath
        if let index = path.lastIndex(of: "/") {
            path = String(path[path.index(index, offsetBy: 1)...])
        }
        return path
    }
}
