import Library
import SwiftUI

public struct GroupListView: View {
    @EnvironmentObject private var environments: ExtensionEnvironments
    @StateObject private var viewModel = GroupListViewModel()

    public init() {}
    public var body: some View {
        VStack {
            #if os(iOS)
            if !Variant.screenshotMode, !environments.serviceAvailable {
                NebulaEmptyState(title: "No active service", message: "Connect a profile to load its outbound groups. Manage profiles from the dashboard.", systemImage: "rectangle.3.group")
            } else if !Variant.screenshotMode, !environments.commandClient.isConnected || environments.commandClient.isReconnecting {
                VStack(spacing: 16) {
                    ProgressView("Waiting for live data")
                    if let error = environments.commandClient.lastError {
                        Text(error).font(.footnote).foregroundStyle(.secondary)
                    }
                }.padding()
            } else if !viewModel.isLoading, viewModel.groups.isEmpty {
                NebulaEmptyState(title: "No outbound groups", message: "This profile has no selectable outbound groups.", systemImage: "rectangle.3.group")
            } else {
                groupList
            }
            #else
            groupList
            #endif
        }
        #if os(iOS)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(NebulaTheme.background)
        #endif
        .environmentObject(viewModel)
        .alert($viewModel.alert)
        .onAppear {
            environments.connect()
            viewModel.connect()
        }
        .onReceive(environments.commandClient.$groups) { groups in
            Task { @MainActor in
                viewModel.setGroups(groups)
            }
        }
    }

    private var groupList: some View {
        Group {
            if viewModel.isLoading {
                ProgressView("Loading...")
            } else {
                ScrollView {
                    LazyVStack(spacing: 0, pinnedViews: [.sectionHeaders]) {
                        ForEach(viewModel.groups, id: \.tag) { group in
                            if group.isExpand {
                                Section {
                                    GroupContentView(group: group)
                                        .padding(.bottom, 14)
                                } header: {
                                    GroupHeaderView(group: group)
                                }
                            } else {
                                GroupHeaderView(group: group)
                                GroupContentView(group: group)
                                    .padding(.bottom, 14)
                            }
                        }
                    }.padding(16)
                }
            }
        }
    }
}
