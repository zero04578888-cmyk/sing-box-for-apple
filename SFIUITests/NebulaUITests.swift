import XCTest

/// Presentation integration checks use the existing snapshot fixture, never a real tunnel or subscription.
@MainActor
final class NebulaUITests: XCTestCase {
    private var app: XCUIApplication!

    private func launch(accessibilitySize: Bool = false) {
        app = XCUIApplication()
        app.launchArguments = ["-FASTLANE_SNAPSHOT", "-AppleLanguages", "(en)", "-AppleLocale", "en_US"]
        if accessibilitySize {
            app.launchArguments += ["-UIPreferredContentSizeCategoryName", "UICTContentSizeCategoryAccessibilityXXXL"]
        }
        app.launchEnvironment["SCREENSHOT_PAGE"] = "dashboard"
        app.launch()
    }

    func testConnectionStateAndDisconnectedStatistics() {
        launch()
        let toggle = app.buttons["nebula.connection.toggle"]
        XCTAssertTrue(toggle.waitForExistence(timeout: 15))
        toggle.tap()
        XCTAssertTrue(app.staticTexts["Disconnected"].waitForExistence(timeout: 10))
        app.tabBars.buttons["Statistics"].tap()
        XCTAssertTrue(app.staticTexts["Waiting for live data"].waitForExistence(timeout: 10))
        XCTAssertFalse(app.staticTexts["249 MB/s"].exists)
        app.tabBars.buttons["Dashboard"].tap()
        toggle.tap()
        XCTAssertTrue(app.staticTexts["Connected"].waitForExistence(timeout: 10))
    }

    func testGroupsAndExistingTabsRemainReachable() {
        launch()
        let groups = app.buttons["nebula.groups.open"]
        // A NavigationLink may be exposed as a button by XCTest.
        XCTAssertTrue(groups.waitForExistence(timeout: 15))
        groups.tap()
        XCTAssertTrue(app.staticTexts["my_group"].waitForExistence(timeout: 10))
        XCTAssertTrue(app.staticTexts["server"].exists)
        for title in ["Dashboard", "Statistics", "Logs", "Tools", "Settings"] {
            XCTAssertTrue(app.tabBars.buttons[title].exists)
        }
        capture("Groups")
    }

    func testStatisticsAndAccessibilityLayout() {
        launch(accessibilitySize: true)
        XCTAssertTrue(app.buttons["nebula.connection.toggle"].waitForExistence(timeout: 15))
        capture("Dashboard-AccessibilityXXXL")
        app.tabBars.buttons["Statistics"].tap()
        XCTAssertTrue(app.staticTexts["Live service statistics"].waitForExistence(timeout: 10))
        XCTAssertTrue(app.staticTexts["Preview data"].exists)
        capture("Statistics-AccessibilityXXXL")
    }

    private func capture(_ name: String) {
        let attachment = XCTAttachment(screenshot: app.screenshot())
        attachment.name = "NEBULA-\(name)"
        attachment.lifetime = .keepAlways
        add(attachment)
    }
}
