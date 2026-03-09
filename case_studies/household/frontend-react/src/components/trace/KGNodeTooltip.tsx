import React from 'react';
import { Tooltip, Box, Text, Stack, Badge, Loader } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';
import client from '../../api/client';

interface KGNodeTooltipProps {
    uri: string;
    label: string;
    children: React.ReactNode;
}

interface KGNodeInfo {
    label: string;
    type: string;
    unit?: string;
    comment?: string;
    value?: string;
}

const KGNodeTooltip: React.FC<KGNodeTooltipProps> = ({ uri, label, children }) => {
    const { data, isLoading } = useQuery<KGNodeInfo | null>({
        queryKey: ['kg-node', uri],
        queryFn: async () => {
            const sparql = `
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX wf: <https://ugentbiomath.github.io/waterframe#>
                SELECT ?label ?type ?unit ?comment ?value WHERE {
                    <${uri}> rdfs:label ?label .
                    OPTIONAL { <${uri}> a ?type }
                    OPTIONAL { <${uri}> rdfs:comment ?comment }
                    OPTIONAL { <${uri}> wf:unit ?unit }
                    OPTIONAL { <${uri}> wf:nominalValue ?value }
                }
                LIMIT 1
            `;
            const { data: resp } = await client.post('/query/sparql', { query: sparql });
            const bindings = resp?.results?.bindings;
            if (!bindings?.length) return null;
            const b = bindings[0];
            const typeUri: string = b.type?.value ?? '';
            return {
                label: b.label?.value ?? label,
                type: typeUri.split('#').pop() ?? typeUri,
                unit: b.unit?.value,
                comment: b.comment?.value,
                value: b.value?.value,
            };
        },
        enabled: !!uri,
        staleTime: 5 * 60 * 1000,
    });

    const tooltipContent = (
        <Stack gap={4} style={{ maxWidth: 220 }}>
            {isLoading ? (
                <Loader size="xs" />
            ) : data ? (
                <>
                    <Text size="xs" fw={600}>{data.label}</Text>
                    {data.type && <Badge size="xs" variant="light">{data.type}</Badge>}
                    {data.unit && <Text size="xs" c="dimmed">Unit: {data.unit}</Text>}
                    {data.value && <Text size="xs" c="dimmed">Value: {data.value}</Text>}
                    {data.comment && <Text size="xs" c="dimmed">{data.comment}</Text>}
                </>
            ) : (
                <Text size="xs" c="dimmed">{label}</Text>
            )}
        </Stack>
    );

    return (
        <Tooltip label={tooltipContent} withinPortal multiline>
            <Box style={{ display: 'inline-block' }}>{children}</Box>
        </Tooltip>
    );
};

export default KGNodeTooltip;
