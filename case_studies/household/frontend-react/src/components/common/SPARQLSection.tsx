import React, { useState } from 'react';
import {
    Tabs,
    TextInput,
    Textarea,
    Button,
    Stack,
    Text,
    Group,
    Paper,
    Table,
    ScrollArea,
    Code,
    SegmentedControl,
    List,
    ThemeIcon,
    Alert
} from '@mantine/core';
import { IconSearch, IconDatabase, IconMessage2, IconSend, IconTable, IconBraces, IconHelp, IconAlertCircle } from '@tabler/icons-react';
import { useSparqlQuery, useNaturalLanguageQuery } from '../../api/queries';

const SAMPLE_SPARQL = [
    {
        label: "List all Entities",
        query: "PREFIX wf: <https://ugentbiomath.github.io/waterframe#>\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\nSELECT ?entity ?type WHERE { \n  ?entity a ?type .\n  FILTER(STRSTARTS(STR(?entity), \"https://w3id.org/waterframe/case/household/\"))\n} LIMIT 10"
    },
    {
        label: "Find MBR System",
        query: "PREFIX wf: <https://ugentbiomath.github.io/waterframe#>\nPREFIX household: <https://w3id.org/waterframe/case/household/>\nSELECT ?mbr WHERE { \n  ?mbr a wf:MembraneBioreactor\n}"
    },
    {
        label: "Water Flow Connections",
        query: "PREFIX wf: <https://ugentbiomath.github.io/waterframe#>\nSELECT ?source ?target WHERE { \n  ?source wf:hasOutputPort ?out .\n  ?out wf:flowsTo ?in .\n  ?target wf:hasInputPort ?in\n} LIMIT 5"
    }
];

const SAMPLE_NL = [
    "What are the components in the household system?",
    "Show me the MBR specifications",
    "How does water flow through the system?"
];

const SPARQLSection: React.FC = () => {
    const [sparqlQuery, setSparqlQuery] = useState('');
    const [nlQuery, setNlQuery] = useState('');
    const [viewMode, setViewMode] = useState<'table' | 'json'>('table');

    const sparqlMutation = useSparqlQuery();
    const nlMutation = useNaturalLanguageQuery();

    const results = sparqlMutation.data?.results || nlMutation.data?.results || [];
    const isExecuting = sparqlMutation.isPending || nlMutation.isPending;
    const error = sparqlMutation.error || nlMutation.error;

    const handleExecute = () => {
        nlMutation.reset();
        sparqlMutation.mutate({ query: sparqlQuery });
    };

    const handleNlSend = () => {
        sparqlMutation.reset();
        nlMutation.mutate({ question: nlQuery });
    };

    const renderTable = (data: unknown) => {
        if (!data) return <Text size="xs" c="dimmed">No results to display.</Text>;

        // Handle standard SPARQL JSON format (container with bindings)
        if (!Array.isArray(data) && typeof data === 'object' && data !== null && 'bindings' in data) {
            const bindings = (data as { bindings?: Array<Record<string, { value?: string }>> }).bindings;
            if (!bindings || bindings.length === 0) return <Text size="xs" c="dimmed">No bindings found.</Text>;

            const vars = sparqlMutation.data?.head?.vars || Object.keys(bindings[0]);

            return (
                <Table verticalSpacing="xs" style={{ fontSize: '11px' }}>
                    <Table.Thead>
                        <Table.Tr>
                            {vars.map((v: string) => <Table.Th key={v}>{v}</Table.Th>)}
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                        {bindings.map((row, i) => (
                            <Table.Tr key={i}>
                                {vars.map((v: string) => (
                                    <Table.Td key={v}>{row[v]?.value ?? String(row[v] ?? '')}</Table.Td>
                                ))}
                            </Table.Tr>
                        ))}
                    </Table.Tbody>
                </Table>
            );
        }

        // Handle simple flat list (often from NL results)
        if (Array.isArray(data) && data.length > 0) {
            const columns = Object.keys(data[0] || {});
            return (
                <Table verticalSpacing="xs" style={{ fontSize: '11px' }}>
                    <Table.Thead>
                        <Table.Tr>
                            {columns.map(col => <Table.Th key={col}>{col}</Table.Th>)}
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                        {data.map((row, i) => {
                            const record = row as Record<string, unknown>;
                            return (
                            <Table.Tr key={i}>
                                {columns.map(col => (
                                    <Table.Td key={col}>
                                        {String((record[col] as { value?: string } | undefined)?.value ?? record[col] ?? '')}
                                    </Table.Td>
                                ))}
                            </Table.Tr>
                            );
                        })}
                    </Table.Tbody>
                </Table>
            );
        }

        return <Text size="xs" c="dimmed">No results found or incompatible format for table view.</Text>;
    };

    return (
        <Paper withBorder shadow="sm" radius="md" p="md" mt="md">
            <Text fw={700} mb="md">Ontology Exploration</Text>

            <Tabs defaultValue="sparql">
                <Tabs.List mb="md">
                    <Tabs.Tab value="sparql" leftSection={<IconDatabase size={16} />}>SPARQL</Tabs.Tab>
                    <Tabs.Tab value="nl" leftSection={<IconMessage2 size={16} />}>Natural Language</Tabs.Tab>
                </Tabs.List>

                <Tabs.Panel value="sparql">
                    <Stack gap="xs">
                        <Text size="xs" fw={500} c="dimmed">Sample Queries:</Text>
                        <Group gap="xs">
                            {SAMPLE_SPARQL.map((q, i) => (
                                <Button key={i} variant="subtle" size="compact-xs" onClick={() => setSparqlQuery(q.query)}>
                                    {q.label}
                                </Button>
                            ))}
                        </Group>
                        <Textarea
                            placeholder="SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
                            minRows={4}
                            value={sparqlQuery}
                            onChange={(e) => setSparqlQuery(e.currentTarget.value)}
                            styles={{ input: { fontFamily: 'monospace' } }}
                        />
                        <Button leftSection={<IconSend size={16} />} onClick={handleExecute} loading={isExecuting}>
                            Execute Query
                        </Button>
                    </Stack>
                </Tabs.Panel>

                <Tabs.Panel value="nl">
                    <Stack gap="xs">
                        <Text size="xs" fw={500} c="dimmed">Try asking:</Text>
                        <List spacing="xs" size="xs" center icon={
                            <ThemeIcon color="blue" size={20} radius="xl">
                                <IconHelp size={12} />
                            </ThemeIcon>
                        }>
                            {SAMPLE_NL.map((q, i) => (
                                <List.Item key={i} style={{ cursor: 'pointer' }} onClick={() => setNlQuery(q)}>
                                    {q}
                                </List.Item>
                            ))}
                        </List>
                        <TextInput
                            placeholder="e.g. What are the components in the household system?"
                            value={nlQuery}
                            onChange={(e) => setNlQuery(e.currentTarget.value)}
                        />
                        <Button variant="light" leftSection={<IconSearch size={16} />} onClick={handleNlSend} loading={isExecuting}>
                            Generate SPARQL
                        </Button>
                    </Stack>
                </Tabs.Panel>
            </Tabs>

            {error && (
                <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red" mt="md">
                    {error.message}
                </Alert>
            )}

            {(sparqlMutation.data || nlMutation.data) && (
                <Stack mt="md" gap="xs">
                    <Group justify="space-between">
                        <Group gap="xs">
                            <Text size="sm" fw={700}>Results</Text>
                            {nlMutation.data?.generated_sparql && (
                                <Text size="xs" c="dimmed" fs="italic">Generated SPARQL from NL</Text>
                            )}
                        </Group>
                        <SegmentedControl
                            size="xs"
                            value={viewMode}
                            onChange={(val) => setViewMode(val as 'table' | 'json')}
                            data={[
                                { label: <Group gap={4}><IconTable size={14} />Table</Group>, value: 'table' },
                                { label: <Group gap={4}><IconBraces size={14} />JSON</Group>, value: 'json' },
                            ]}
                        />
                    </Group>

                    {viewMode === 'table' ? (
                        <ScrollArea h={200} offsetScrollbars>
                            {renderTable(results)}
                        </ScrollArea>
                    ) : (
                        <ScrollArea h={200} offsetScrollbars>
                            <Code block>{JSON.stringify(results, null, 2)}</Code>
                        </ScrollArea>
                    )}
                </Stack>
            )}
        </Paper>
    );
};

export default SPARQLSection;
