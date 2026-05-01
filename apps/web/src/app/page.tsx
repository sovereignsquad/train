import {
  Badge,
  Button,
  Card,
  Code,
  Container,
  Divider,
  Grid,
  Group,
  List,
  Paper,
  SimpleGrid,
  Stack,
  Table,
  Text,
  Title,
} from "@mantine/core";
import { revalidatePath } from "next/cache";

import { getApiBaseUrl, getDashboardData } from "@/lib/api";
import { ThemeToggle } from "./ThemeToggle";

export const dynamic = "force-dynamic";

async function resumeRunAction(formData: FormData) {
  "use server";

  const runId = formData.get("runId");
  if (typeof runId !== "string" || !runId) {
    throw new Error("Missing run id");
  }

  const response = await fetch(`${getApiBaseUrl()}/v1/runs/${runId}/resume`, {
    method: "POST",
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Resume failed: ${response.status} ${response.statusText}`);
  }

  revalidatePath("/");
}

function MetricValue({ value }: { value: number | null }) {
  if (value === null) {
    return <Text c="dimmed">n/a</Text>;
  }

  return <Code>{value.toFixed(6)}</Code>;
}

function StatusBadge({ value }: { value: string | boolean | null }) {
  if (typeof value === "boolean") {
    const tone = value ? "success" : "neutral";
    return <Badge className={`status-badge status-badge--${tone}`}>{value ? "yes" : "no"}</Badge>;
  }

  if (value === null) {
    return <Badge className="status-badge status-badge--neutral">n/a</Badge>;
  }

  const normalized = value.toLowerCase();
  const tone =
    normalized === "accepted" || normalized === "succeeded" || normalized === "ok"
      ? "success"
      : normalized === "rejected"
        ? "warning"
        : normalized === "failed" || normalized === "blocked"
          ? "danger"
          : normalized === "resume" || normalized === "running" || normalized === "reachable"
            ? "info"
            : "neutral";

  return <Badge className={`status-badge status-badge--${tone}`}>{value}</Badge>;
}

function ErrorBlock({ title, message }: { title: string; message: string | null }) {
  return (
    <Card className="panel" padding="lg" radius="xl">
      <Stack gap="xs">
        <Text fw={700}>{title}</Text>
        <Text c="dimmed" size="sm">
          {message || "No data available"}
        </Text>
      </Stack>
    </Card>
  );
}

export default async function Home() {
  const data = await getDashboardData();
  const runs = data.runs.data ?? [];
  const states = data.projectStates.data ?? [];
  const projects = data.projects.data ?? [];
  const health = data.health.data;
  const agent = data.agentStatus.data;
  const operator = data.operatorStatus.data;
  const providers = [
    { key: "mistral", result: data.providers.mistral },
    { key: "ollama", result: data.providers.ollama },
  ];

  return (
    <main className="page-shell">
      <Container size="xl" py={48}>
        <Stack gap="xl">
          <Paper className="hero" radius="xl" p="xl">
            <Group justify="space-between" align="flex-start" gap="xl">
              <Stack gap="md" maw={760}>
                <Badge className="status-badge status-badge--warning" size="lg" variant="light">
                  train operator surface
                </Badge>
                <Title order={1} size={44} lh={1.02}>
                  Local control surface for the autonomous experiment engine.
                </Title>
                <Text size="lg" c="dimmed">
                  This UI is intentionally narrow: it exposes health, projects, runs, ratchet
                  outcomes, recovery signals, and the first agent adapter without inventing a
                  second source of truth.
                </Text>
              </Stack>
              <Stack gap="xs" miw={260}>
                <Group justify="flex-end">
                  <div className="theme-toggle-shell">
                    <Text className="section-label">Theme</Text>
                    <ThemeToggle />
                  </div>
                </Group>
                <Text tt="uppercase" fz={12} fw={700} c="dimmed">
                  API base URL
                </Text>
                <Text ff="monospace" size="sm">
                  {data.apiBaseUrl}
                </Text>
              </Stack>
            </Group>
          </Paper>

          <SimpleGrid cols={{ base: 1, md: 4 }} spacing="lg">
            <Card className="panel metric-card" radius="xl" padding="lg">
              <Text className="metric-card__label">
                Service
              </Text>
              <Title order={3}>{health?.service ?? "unavailable"}</Title>
              <Group gap="xs" mt="sm">
                <StatusBadge value={health?.status ?? "offline"} />
                <Badge variant="outline">{health?.environment ?? "unknown"}</Badge>
              </Group>
            </Card>
            <Card className="panel metric-card" radius="xl" padding="lg">
              <Text className="metric-card__label">
                Registered Projects
              </Text>
              <Title order={3}>{projects.length}</Title>
              <Text size="sm" c="dimmed" mt="sm">
                Bound by a single mutable artifact and one machine-readable score.
              </Text>
            </Card>
            <Card className="panel metric-card" radius="xl" padding="lg">
              <Text className="metric-card__label">
                Runs Logged
              </Text>
              <Title order={3}>{runs.length}</Title>
              <Text size="sm" c="dimmed" mt="sm">
                Lifecycle + ratchet state persisted in local SQLite.
              </Text>
            </Card>
            <Card className="panel metric-card" radius="xl" padding="lg">
              <Text className="metric-card__label">
                Recovery
              </Text>
              <Title order={3}>{operator?.recoverable_runs.length ?? 0}</Title>
              <Text size="sm" c="dimmed" mt="sm">
                Recoverable runs derived from durable heartbeat and lease state.
              </Text>
            </Card>
            <Card className="panel metric-card" radius="xl" padding="lg">
              <Text className="metric-card__label">
                Agent Adapter
              </Text>
              <Title order={3}>{agent?.name ?? "unknown"}</Title>
              <Group gap="xs" mt="sm">
                <StatusBadge value={agent?.available ?? false} />
                <StatusBadge value={agent?.mistral_api_key_configured ?? false} />
              </Group>
            </Card>
          </SimpleGrid>

          <Grid gap="lg">
            <Grid.Col span={{ base: 12, lg: 7 }}>
              {data.runs.ok ? (
                <Card className="panel section-panel" radius="xl" padding="lg">
                  <Group justify="space-between" mb="md">
                    <div>
                      <Title order={3}>Recent Runs</Title>
                      <Text c="dimmed" size="sm">
                        Execution and ratchet outcomes from the backend ledger.
                      </Text>
                    </div>
                    <Badge variant="outline">{runs.length} total</Badge>
                  </Group>
                  <Table stickyHeader stickyHeaderOffset={0} highlightOnHover>
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>ID</Table.Th>
                        <Table.Th>Project</Table.Th>
                        <Table.Th>Status</Table.Th>
                        <Table.Th>Ratchet</Table.Th>
                        <Table.Th>Metric</Table.Th>
                        <Table.Th>Git</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {runs.map((run) => (
                        <Table.Tr key={run.id}>
                          <Table.Td>
                            <Code>{run.id}</Code>
                          </Table.Td>
                          <Table.Td>
                            <Stack gap={2}>
                              <Text fw={600}>{run.title}</Text>
                              <Text size="xs" c="dimmed">
                                {run.project_key}
                              </Text>
                            </Stack>
                          </Table.Td>
                          <Table.Td>
                            <StatusBadge value={run.status} />
                          </Table.Td>
                          <Table.Td>
                            <StatusBadge value={run.ratchet_decision} />
                          </Table.Td>
                          <Table.Td>
                            <MetricValue value={run.metric_value} />
                          </Table.Td>
                          <Table.Td>
                            <StatusBadge value={run.git_action} />
                          </Table.Td>
                        </Table.Tr>
                      ))}
                    </Table.Tbody>
                  </Table>
                </Card>
              ) : (
                <ErrorBlock title="Recent Runs" message={data.runs.error} />
              )}
            </Grid.Col>
            <Grid.Col span={{ base: 12, lg: 5 }}>
              <Stack gap="lg">
                {data.projectStates.ok ? (
                  <Card className="panel section-panel" radius="xl" padding="lg">
                    <Title order={3}>Project State</Title>
                    <Text c="dimmed" size="sm" mb="md">
                      Best-so-far state that drives the ratchet.
                    </Text>
                    <Stack gap="md">
                      {states.map((state) => (
                        <Paper key={state.project_key} className="panel-alt" radius="lg" p="md">
                          <Group justify="space-between" align="center">
                            <div>
                              <Text fw={700}>{state.project_key}</Text>
                              <Text size="sm" c="dimmed">
                                {state.metric_name} / {state.metric_direction}
                              </Text>
                            </div>
                            <StatusBadge value={state.git_worktree_dirty} />
                          </Group>
                          <Divider my="sm" />
                          <Group grow>
                            <div>
                              <Text className="section-label">
                                Best run
                              </Text>
                              <Text fw={700}>{state.best_run_id ?? "n/a"}</Text>
                            </div>
                            <div>
                              <Text className="section-label">
                                Best metric
                              </Text>
                              <MetricValue value={state.best_metric_value} />
                            </div>
                          </Group>
                        </Paper>
                      ))}
                    </Stack>
                  </Card>
                ) : (
                  <ErrorBlock title="Project State" message={data.projectStates.error} />
                )}

                {data.operatorStatus.ok && operator ? (
                  <Card className="panel section-panel" radius="xl" padding="lg">
                    <Title order={3}>Operator Status</Title>
                    <Text c="dimmed" size="sm" mb="md">
                      Durable health signals for unattended sessions and safe resume planning.
                    </Text>
                    <Group grow mb="md">
                        <Paper className="panel-alt" radius="lg" p="md">
                          <Text className="section-label">
                            Running
                          </Text>
                        <Text fw={700}>{operator.running_runs}</Text>
                      </Paper>
                        <Paper className="panel-alt" radius="lg" p="md">
                          <Text className="section-label">
                            Healthy
                          </Text>
                        <Text fw={700}>{operator.healthy_running_runs}</Text>
                      </Paper>
                        <Paper className="panel-alt" radius="lg" p="md">
                          <Text className="section-label">
                            Stalled
                          </Text>
                        <Text fw={700}>{operator.stalled_runs}</Text>
                      </Paper>
                    </Group>
                    {operator.recoverable_runs.length ? (
                      <Stack gap="md">
                        {operator.recoverable_runs.map((run) => (
                          <Paper key={run.id} className="panel-alt" radius="lg" p="md">
                            <Group justify="space-between" align="center">
                              <div>
                                <Text fw={700}>{run.title}</Text>
                                <Text size="sm" c="dimmed">
                                  {run.project_key} / checkpoint {run.best_run_id ?? "n/a"}
                                </Text>
                              </div>
                              <Group gap="xs">
                                <StatusBadge value={run.status} />
                                <StatusBadge value={run.stalled} />
                              </Group>
                            </Group>
                            <Text size="sm" c="dimmed" mt="sm">
                              resume_count={run.resume_count} lease_expires_at=
                              {run.lease_expires_at ?? "n/a"}
                            </Text>
                            {run.error_message ? (
                              <Text size="sm" mt="sm">
                                {run.error_message}
                              </Text>
                            ) : null}
                            <form action={resumeRunAction}>
                              <input type="hidden" name="runId" value={run.id} />
                              <Button className="resume-button" mt="md" radius="xl" size="xs" type="submit">
                                Resume From Checkpoint
                              </Button>
                            </form>
                          </Paper>
                        ))}
                      </Stack>
                    ) : (
                      <Text c="dimmed" size="sm">
                        No recoverable runs currently require operator action.
                      </Text>
                    )}
                  </Card>
                ) : (
                  <ErrorBlock title="Operator Status" message={data.operatorStatus.error} />
                )}

                {data.agentStatus.ok ? (
                  <Card className="panel section-panel" radius="xl" padding="lg">
                    <Title order={3}>Vibe Adapter</Title>
                    <Text c="dimmed" size="sm" mb="md">
                      Canonical bootstrap surface for the first supported agent adapter.
                    </Text>
                    <List spacing="xs" size="sm">
                      <List.Item>
                        Executable: <span className="code-pill">{agent?.resolved_executable ?? agent?.executable}</span>
                      </List.Item>
                      <List.Item>
                        Version: <span className="code-pill">{agent?.version ?? "unknown"}</span>
                      </List.Item>
                      <List.Item>
                        Contract home: <span className="code-pill">{agent?.contract_home ?? "unknown"}</span>
                      </List.Item>
                      <List.Item>
                        Runtime home: <span className="code-pill">{agent?.runtime_home ?? "unknown"}</span>
                      </List.Item>
                    </List>
                    {agent?.issues.length ? (
                      <>
                        <Divider my="md" />
                        <List className="issue-list" spacing="xs" size="sm">
                          {agent.issues.map((issue) => (
                            <List.Item key={issue}>{issue}</List.Item>
                          ))}
                        </List>
                      </>
                    ) : null}
                  </Card>
                ) : (
                  <ErrorBlock title="Vibe Adapter" message={data.agentStatus.error} />
                )}

                <Card className="panel section-panel" radius="xl" padding="lg">
                  <Title order={3}>Providers</Title>
                  <Text c="dimmed" size="sm" mb="md">
                    Hosted and local model backends stay below the engine contract.
                  </Text>
                  <Stack gap="md">
                    {providers.map((provider) =>
                      provider.result.ok && provider.result.data ? (
                        <Paper
                          key={provider.result.data.key}
                          className="panel-alt"
                          radius="lg"
                          p="md"
                        >
                          <Group justify="space-between" align="center">
                            <div>
                              <Text fw={700}>{provider.result.data.name}</Text>
                              <Text size="sm" c="dimmed">
                                {provider.result.data.kind} / {provider.result.data.base_url}
                              </Text>
                            </div>
                            <StatusBadge value={provider.result.data.reachable} />
                          </Group>
                          <Group gap="xs" mt="sm">
                            <Badge variant="outline">
                              configured: {provider.result.data.configured ? "yes" : "no"}
                            </Badge>
                            <Badge variant="outline">
                              models: {provider.result.data.model_count ?? "n/a"}
                            </Badge>
                          </Group>
                          {provider.result.data.models.length ? (
                            <Text size="sm" c="dimmed" mt="sm">
                              {provider.result.data.models.slice(0, 3).join(", ")}
                            </Text>
                          ) : null}
                          {provider.result.data.issues.length ? (
                            <List spacing="xs" size="sm" mt="sm">
                              {provider.result.data.issues.map((issue) => (
                                <List.Item key={issue}>{issue}</List.Item>
                              ))}
                            </List>
                          ) : null}
                        </Paper>
                      ) : (
                        <ErrorBlock
                          key={provider.key}
                          title="Provider"
                          message={provider.result.error}
                        />
                      ),
                    )}
                  </Stack>
                </Card>
              </Stack>
            </Grid.Col>
          </Grid>
        </Stack>
      </Container>
    </main>
  );
}
