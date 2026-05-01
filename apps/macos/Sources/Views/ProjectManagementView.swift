import AppKit
import SwiftUI

struct ProjectManagementView: View {
    @EnvironmentObject private var viewModel: AppViewModel

    @State private var editorState = ProjectEditorState.blank()
    @State private var isPresentingEditor = false
    @State private var editingProjectKey: String?
    @State private var deleteCandidate: ProjectPayload?
    @State private var selectedProjectKey: String?

    private var managedProjects: [ProjectPayload] {
        viewModel.projects.filter { $0.sourceKind == "managed" }
    }

    private var referenceProjects: [ProjectPayload] {
        viewModel.projects.filter { $0.sourceKind == "reference" }
    }

    private var selectedProject: ProjectPayload? {
        viewModel.projects.first(where: { $0.key == selectedProjectKey })
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Projects")
                        .font(.title2)
                        .fontWeight(.bold)
                    Text("Use the list to select a project. Managed projects and reference templates are separated.")
                        .foregroundStyle(.secondary)
                }
                Spacer()
                Button("New Project") {
                    editingProjectKey = nil
                    editorState = .blank()
                    isPresentingEditor = true
                }
            }

            HSplitView {
                projectListPane
                    .frame(minWidth: 280, idealWidth: 340, maxWidth: 380)
                projectDetailPane
                    .frame(minWidth: 440, maxWidth: .infinity, maxHeight: .infinity)
            }
        }
        .onAppear {
            if selectedProjectKey == nil {
                selectedProjectKey = managedProjects.first?.key ?? referenceProjects.first?.key
            }
        }
        .sheet(isPresented: $isPresentingEditor) {
            ProjectEditorSheet(
                title: editingProjectKey == nil ? "Create Project" : "Edit Project",
                state: $editorState,
                isEditing: editingProjectKey != nil,
                repositoryRoot: viewModel.processSupervisor.repositoryRoot,
                referenceProjects: referenceProjects,
                onSubmit: submitEditor
            )
            .frame(minWidth: 720, minHeight: 620)
        }
        .alert(item: $deleteCandidate) { project in
            Alert(
                title: Text("Delete \(project.name)?"),
                message: Text("This removes the managed project definition from train."),
                primaryButton: .destructive(Text("Delete")) {
                    viewModel.deleteProject(project.key)
                    if selectedProjectKey == project.key {
                        selectedProjectKey = managedProjects.first(where: { $0.key != project.key })?.key
                    }
                },
                secondaryButton: .cancel()
            )
        }
    }

    private var projectListPane: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Project List")
                .font(.headline)
            Text("Choose from a native list instead of scrolling through long cards.")
                .font(.caption)
                .foregroundStyle(.secondary)

            List(selection: $selectedProjectKey) {
                Section("Managed Projects") {
                    if managedProjects.isEmpty {
                        Text("No managed projects yet")
                            .foregroundStyle(.secondary)
                    } else {
                        ForEach(managedProjects) { project in
                            projectRow(project)
                                .tag(project.key)
                        }
                    }
                }

                Section("Reference Templates") {
                    ForEach(referenceProjects) { project in
                        projectRow(project)
                            .tag(project.key)
                    }
                }
            }
        }
    }

    private var projectDetailPane: some View {
        GroupBox {
            if let selectedProject {
                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        detailHeader(for: selectedProject)
                        executionSection(for: selectedProject)
                        artifactSection(for: selectedProject)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                }
            } else {
                VStack(alignment: .leading, spacing: 10) {
                    Text("No Project Selected")
                        .font(.headline)
                    Text("Select a managed project or template from the list.")
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
            }
        }
    }

    private func projectRow(_ project: ProjectPayload) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(project.name)
                .fontWeight(.semibold)
            Text(project.key)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }

    private func detailHeader(for project: ProjectPayload) -> some View {
        HStack(alignment: .top) {
            VStack(alignment: .leading, spacing: 6) {
                Text(project.name)
                    .font(.title3)
                    .fontWeight(.bold)
                Text(project.sourceKind == "reference" ? "Reference Template" : "Managed Project")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(project.description)
                    .font(.body)
                    .foregroundStyle(.secondary)
                    .textSelection(.enabled)
            }
            Spacer()
            HStack {
                if project.sourceKind == "reference" {
                    Button("Use Template") {
                        editingProjectKey = nil
                        editorState = .fromTemplate(project)
                        isPresentingEditor = true
                    }
                } else {
                    Button("Edit") {
                        editingProjectKey = project.key
                        editorState = .fromProject(project)
                        isPresentingEditor = true
                    }
                    Button("Delete", role: .destructive) {
                        deleteCandidate = project
                    }
                }
            }
        }
    }

    private func executionSection(for project: ProjectPayload) -> some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 10) {
                infoRow("Metric", "\(project.metricName) / \(project.metricDirection)")
                infoRow(
                    "Budget",
                    "\(project.minBudgetSeconds)s - \(project.defaultBudgetSeconds)s - \(project.maxBudgetSeconds)s"
                )
                infoRow("Runner", project.runnerKey)
                infoRow("Mutable Artifact", project.mutableArtifact)
                infoRow("Entrypoint", project.executionEntrypoint)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Text("Execution Contract")
                .font(.headline)
        }
    }

    private func artifactSection(for project: ProjectPayload) -> some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 12) {
                artifactReadList("Autonomous Mutable Artifacts", items: project.autonomousMutableArtifacts)
                artifactReadList("Setup Artifacts", items: project.setupArtifacts)
                artifactReadList("Dependency Artifacts", items: project.dependencyArtifacts)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        } label: {
            Text("Artifacts")
                .font(.headline)
        }
    }

    private func artifactReadList(_ title: String, items: [String]) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .fontWeight(.semibold)
            ForEach(items, id: \.self) { item in
                Text(item)
                    .font(.caption)
                    .padding(.vertical, 4)
                    .padding(.horizontal, 8)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.secondary.opacity(0.08))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                    .textSelection(.enabled)
            }
        }
    }

    private func submitEditor() {
        let payload = editorState.toPayload()
        if let editingProjectKey {
            viewModel.updateProject(editingProjectKey, payload: payload)
            selectedProjectKey = editingProjectKey
        } else {
            viewModel.createProject(payload)
            selectedProjectKey = payload.key
        }
        isPresentingEditor = false
    }

    private func infoRow(_ label: String, _ value: String) -> some View {
        HStack(alignment: .top, spacing: 12) {
            Text(label)
                .font(.caption)
                .foregroundStyle(.secondary)
                .frame(width: 120, alignment: .leading)
            Text(value)
                .font(.caption)
                .textSelection(.enabled)
            Spacer()
        }
    }
}

private struct ProjectEditorSheet: View {
    let title: String
    @Binding var state: ProjectEditorState
    let isEditing: Bool
    let repositoryRoot: URL?
    let referenceProjects: [ProjectPayload]
    let onSubmit: () -> Void

    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            VStack(alignment: .leading, spacing: 6) {
                Text(title)
                    .font(.title3)
                    .fontWeight(.bold)
                Text("Use the native selectors for files and the list editors for multi-value artifact fields.")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    editorSection("Identity", subtitle: "Basic naming and project purpose.") {
                        ResponsiveFormRow(
                            title: "Key",
                            help: "Stable project identifier used by the engine and API."
                        ) {
                            TextField("my-project", text: $state.key)
                                .disabled(isEditing)
                        }
                        ResponsiveFormRow(
                            title: "Name",
                            help: "Human-readable project name."
                        ) {
                            TextField("Project Name", text: $state.name)
                        }
                        ResponsiveFormRow(
                            title: "Description",
                            help: "Explain what this project optimizes."
                        ) {
                            TextEditor(text: $state.description)
                                .font(.body)
                                .frame(minHeight: 96)
                                .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.secondary.opacity(0.2)))
                        }
                    }

                    editorSection("Execution", subtitle: "Metric, runner, and entrypoint configuration.") {
                        ResponsiveFormRow(
                            title: "Metric Name",
                            help: "One machine-readable metric the engine will optimize."
                        ) {
                            TextField("val_bpb", text: $state.metricName)
                        }
                        ResponsiveFormRow(
                            title: "Metric Direction",
                            help: "Choose whether lower or higher metric values are better."
                        ) {
                            Picker("Metric Direction", selection: $state.metricDirection) {
                                Text("minimize").tag("minimize")
                                Text("maximize").tag("maximize")
                            }
                            .pickerStyle(.menu)
                            .frame(maxWidth: 220, alignment: .leading)
                        }
                        ResponsiveFormRow(
                            title: "Runner Key",
                            help: "Execution adapter used for the benchmark contract."
                        ) {
                            Picker("Runner Key", selection: $state.runnerKey) {
                                Text("python-benchmark").tag("python-benchmark")
                            }
                            .pickerStyle(.menu)
                            .frame(maxWidth: 220, alignment: .leading)
                        }
                        ResponsiveFormRow(
                            title: "Execution Entrypoint",
                            help: "The benchmark script the engine executes for a bounded run."
                        ) {
                            FileFieldRow(
                                value: $state.executionEntrypoint,
                                placeholder: "projects/my-project/run_benchmark.py",
                                repositoryRoot: repositoryRoot
                            )
                        }
                        ResponsiveFormRow(
                            title: "Template",
                            help: "Optional reference template this managed project was derived from."
                        ) {
                            Picker("Template", selection: $state.templateKey) {
                                Text("None").tag(String?.none)
                                ForEach(referenceProjects) { project in
                                    Text(project.name).tag(String?.some(project.key))
                                }
                            }
                            .pickerStyle(.menu)
                            .frame(maxWidth: 320, alignment: .leading)
                        }
                    }

                    editorSection("Budget", subtitle: "Bounded runtime budget for comparable experiments.") {
                        ResponsiveBudgetEditor(
                            minBudgetSeconds: $state.minBudgetSeconds,
                            defaultBudgetSeconds: $state.defaultBudgetSeconds,
                            maxBudgetSeconds: $state.maxBudgetSeconds
                        )
                    }

                    editorSection("Artifacts", subtitle: "Select concrete repo files instead of typing raw multiline text.") {
                        ResponsiveFormRow(
                            title: "Mutable Artifact",
                            help: "Primary file the agent is allowed to change."
                        ) {
                            FileFieldRow(
                                value: $state.mutableArtifact,
                                placeholder: "projects/my-project/train.py",
                                repositoryRoot: repositoryRoot
                            )
                        }
                        ArtifactListEditor(
                            title: "Autonomous Mutable Artifacts",
                            help: "Additional files the agent can edit. Use the list controls instead of newline text.",
                            repositoryRoot: repositoryRoot,
                            items: $state.autonomousMutableArtifacts
                        )
                        ArtifactListEditor(
                            title: "Setup Artifacts",
                            help: "Files the agent must not mutate because they define setup and evaluation.",
                            repositoryRoot: repositoryRoot,
                            items: $state.setupArtifacts
                        )
                        ArtifactListEditor(
                            title: "Dependency Artifacts",
                            help: "Dependency or environment files that remain protected during autonomous runs.",
                            repositoryRoot: repositoryRoot,
                            items: $state.dependencyArtifacts
                        )
                    }
                }
                .padding(.trailing, 8)
            }

            HStack {
                Spacer()
                Button("Cancel") {
                    dismiss()
                }
                Button(isEditing ? "Save Project" : "Create Project") {
                    onSubmit()
                }
                .buttonStyle(.borderedProminent)
                .disabled(!state.isValid)
            }
        }
        .padding(20)
    }

    private func editorSection<Content: View>(_ title: String, subtitle: String, @ViewBuilder content: () -> Content) -> some View {
        GroupBox {
            VStack(alignment: .leading, spacing: 14) {
                Text(title)
                    .font(.headline)
                Text(subtitle)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                content()
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

private struct ResponsiveFormRow<Content: View>: View {
    let title: String
    let help: String
    @ViewBuilder let content: () -> Content

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(alignment: .top, spacing: 16) {
                labelBlock
                    .frame(width: 220, alignment: .leading)
                content()
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            VStack(alignment: .leading, spacing: 8) {
                labelBlock
                content()
            }
        }
    }

    private var labelBlock: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .fontWeight(.semibold)
            Text(help)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }
}

private struct FileFieldRow: View {
    @Binding var value: String
    let placeholder: String
    let repositoryRoot: URL?

    var body: some View {
        HStack(spacing: 10) {
            TextField(placeholder, text: $value)
                .textSelection(.enabled)
            Button("Browse") {
                if let selection = chooseRelativePaths(from: repositoryRoot, allowsMultipleSelection: false).first {
                    value = selection
                }
            }
            .disabled(repositoryRoot == nil)
        }
    }
}

private struct ArtifactListEditor: View {
    let title: String
    let help: String
    let repositoryRoot: URL?
    @Binding var items: [String]

    @State private var selectedIndex: Int?

    var body: some View {
        ResponsiveFormRow(title: title, help: help) {
            VStack(alignment: .leading, spacing: 10) {
                List(selection: $selectedIndex) {
                    ForEach(Array(items.enumerated()), id: \.offset) { index, _ in
                        TextField("project/file.py", text: binding(for: index))
                            .textSelection(.enabled)
                            .tag(index)
                    }
                }
                .frame(minHeight: 120, maxHeight: 180)

                HStack {
                    Button("Add File") {
                        let selections = chooseRelativePaths(from: repositoryRoot, allowsMultipleSelection: true)
                        for selection in selections where items.contains(selection) == false {
                            items.append(selection)
                        }
                    }
                    .disabled(repositoryRoot == nil)

                    Button("Add Empty Row") {
                        items.append("")
                        selectedIndex = items.indices.last
                    }

                    Button("Remove Selected") {
                        guard let selectedIndex, items.indices.contains(selectedIndex) else { return }
                        items.remove(at: selectedIndex)
                        self.selectedIndex = nil
                    }
                    .disabled(selectedIndex == nil)

                    Spacer()

                    Text("\(items.filter { !$0.trimmed().isEmpty }.count) entries")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
            }
        }
    }

    private func binding(for index: Int) -> Binding<String> {
        Binding(
            get: { items[index] },
            set: { items[index] = $0 }
        )
    }
}

private struct ResponsiveBudgetEditor: View {
    @Binding var minBudgetSeconds: Int
    @Binding var defaultBudgetSeconds: Int
    @Binding var maxBudgetSeconds: Int

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(spacing: 16) {
                budgetField("Min Budget", value: $minBudgetSeconds)
                budgetField("Default Budget", value: $defaultBudgetSeconds)
                budgetField("Max Budget", value: $maxBudgetSeconds)
            }
            VStack(spacing: 12) {
                budgetField("Min Budget", value: $minBudgetSeconds)
                budgetField("Default Budget", value: $defaultBudgetSeconds)
                budgetField("Max Budget", value: $maxBudgetSeconds)
            }
        }
    }

    private func budgetField(_ title: String, value: Binding<Int>) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Text(title)
                .fontWeight(.semibold)
            TextField(title, value: value, format: .number)
                .frame(maxWidth: .infinity)
        }
    }
}

private struct ProjectEditorState {
    var key: String
    var name: String
    var description: String
    var mutableArtifact: String
    var autonomousMutableArtifacts: [String]
    var setupArtifacts: [String]
    var dependencyArtifacts: [String]
    var metricName: String
    var metricDirection: String
    var minBudgetSeconds: Int
    var defaultBudgetSeconds: Int
    var maxBudgetSeconds: Int
    var runnerKey: String
    var executionEntrypoint: String
    var templateKey: String?

    var isValid: Bool {
        !key.trimmed().isEmpty &&
        !name.trimmed().isEmpty &&
        !description.trimmed().isEmpty &&
        !mutableArtifact.trimmed().isEmpty &&
        !metricName.trimmed().isEmpty &&
        !runnerKey.trimmed().isEmpty &&
        !executionEntrypoint.trimmed().isEmpty &&
        cleaned(autonomousMutableArtifacts).isEmpty == false &&
        cleaned(setupArtifacts).isEmpty == false &&
        cleaned(dependencyArtifacts).isEmpty == false &&
        minBudgetSeconds <= defaultBudgetSeconds &&
        defaultBudgetSeconds <= maxBudgetSeconds
    }

    static func blank() -> ProjectEditorState {
        ProjectEditorState(
            key: "",
            name: "",
            description: "",
            mutableArtifact: "",
            autonomousMutableArtifacts: [],
            setupArtifacts: [],
            dependencyArtifacts: ["pyproject.toml", "uv.lock"],
            metricName: "",
            metricDirection: "minimize",
            minBudgetSeconds: 60,
            defaultBudgetSeconds: 300,
            maxBudgetSeconds: 300,
            runnerKey: "python-benchmark",
            executionEntrypoint: "",
            templateKey: nil
        )
    }

    static func fromProject(_ project: ProjectPayload) -> ProjectEditorState {
        ProjectEditorState(
            key: project.key,
            name: project.name,
            description: project.description,
            mutableArtifact: project.mutableArtifact,
            autonomousMutableArtifacts: project.autonomousMutableArtifacts,
            setupArtifacts: project.setupArtifacts,
            dependencyArtifacts: project.dependencyArtifacts,
            metricName: project.metricName,
            metricDirection: project.metricDirection,
            minBudgetSeconds: project.minBudgetSeconds,
            defaultBudgetSeconds: project.defaultBudgetSeconds,
            maxBudgetSeconds: project.maxBudgetSeconds,
            runnerKey: project.runnerKey,
            executionEntrypoint: project.executionEntrypoint,
            templateKey: project.templateKey
        )
    }

    static func fromTemplate(_ project: ProjectPayload) -> ProjectEditorState {
        ProjectEditorState(
            key: "",
            name: "\(project.name) Copy",
            description: project.description,
            mutableArtifact: project.mutableArtifact,
            autonomousMutableArtifacts: project.autonomousMutableArtifacts,
            setupArtifacts: project.setupArtifacts,
            dependencyArtifacts: project.dependencyArtifacts,
            metricName: project.metricName,
            metricDirection: project.metricDirection,
            minBudgetSeconds: project.minBudgetSeconds,
            defaultBudgetSeconds: project.defaultBudgetSeconds,
            maxBudgetSeconds: project.maxBudgetSeconds,
            runnerKey: project.runnerKey,
            executionEntrypoint: project.executionEntrypoint,
            templateKey: project.templateKey ?? project.key
        )
    }

    func toPayload() -> ProjectWritePayload {
        let normalizedTemplateKey = templateKey?.trimmed()
        return ProjectWritePayload(
            key: key.trimmed(),
            name: name.trimmed(),
            description: description.trimmed(),
            mutableArtifact: mutableArtifact.trimmed(),
            autonomousMutableArtifacts: cleaned(autonomousMutableArtifacts),
            setupArtifacts: cleaned(setupArtifacts),
            dependencyArtifacts: cleaned(dependencyArtifacts),
            metricName: metricName.trimmed(),
            metricDirection: metricDirection,
            minBudgetSeconds: minBudgetSeconds,
            defaultBudgetSeconds: defaultBudgetSeconds,
            maxBudgetSeconds: maxBudgetSeconds,
            runnerKey: runnerKey.trimmed(),
            executionEntrypoint: executionEntrypoint.trimmed(),
            templateKey: normalizedTemplateKey?.isEmpty == true ? nil : normalizedTemplateKey
        )
    }

    private func cleaned(_ values: [String]) -> [String] {
        values
            .map { $0.trimmed() }
            .filter { !$0.isEmpty }
    }
}

@MainActor
private func chooseRelativePaths(from repositoryRoot: URL?, allowsMultipleSelection: Bool) -> [String] {
    guard let repositoryRoot else { return [] }

    let panel = NSOpenPanel()
    panel.directoryURL = repositoryRoot
    panel.canChooseFiles = true
    panel.canChooseDirectories = false
    panel.allowsMultipleSelection = allowsMultipleSelection
    panel.resolvesAliases = true

    let response = panel.runModal()
    guard response == .OK else { return [] }

    return panel.urls.map { url in
        let path = url.path
        let rootPath = repositoryRoot.path.hasSuffix("/") ? repositoryRoot.path : repositoryRoot.path + "/"
        if path.hasPrefix(rootPath) {
            return String(path.dropFirst(rootPath.count))
        }
        return path
    }
}

private extension String {
    func trimmed() -> String {
        trimmingCharacters(in: .whitespacesAndNewlines)
    }
}
