import React from 'react';
import {
    Stack,
    Title,
    Text,
    Badge,
    Divider,
    LoadingOverlay,
    Box,
    Group,
    Breadcrumbs,
    Anchor,
    Table,
    ScrollArea,
    ActionIcon
} from '@mantine/core';
import { IconChevronLeft, IconChevronRight } from '@tabler/icons-react';
import { useSelectionStore } from '../../stores/useSelectionStore';
import { useEntityState, useEntityTriplets } from '../../api/queries';

const EntityDetails: React.FC = () => {
    const { selectedEntityId, history, popSelection, pushSelection } = useSelectionStore();
    const { data: entity, isLoading: isStateLoading } = useEntityState(selectedEntityId);
    const { data: triplets, isLoading: isTripletsLoading } = useEntityTriplets(selectedEntityId);

    const isLoading = isStateLoading || isTripletsLoading;

    if (!selectedEntityId) {
        return (
            <Box p="md">
                <Text c="dimmed" fs="italic">Select an entity on the map or graph to view details.</Text>
            </Box>
        );
    }

    const normalizeEntityId = (value: string) => {
        if (!value) return value;
        return value.split('/').pop()?.split('#').pop() || value;
    };

    const breadcrumbItems = history.map((id, index) => (
        <Anchor
            key={index}
            size="xs"
            onClick={() => {
                // To jump back to a specific point in history, we'd need a specific action.
                // For now, let's just show the last few? 
                // Actually, let's just show "Back" and the current label.
            }}
            style={{ fontWeight: index === history.length - 1 ? 700 : 400 }}
        >
            {normalizeEntityId(id)}
        </Anchor>
    ));

    return (
        <Box p="md" style={{ position: 'relative', height: '100%' }}>
            <LoadingOverlay visible={isLoading} />

            <Stack gap="xs">
                {history.length > 1 && (
                    <Group gap="xs" mb="xs">
                        <ActionIcon variant="subtle" size="sm" onClick={popSelection}>
                            <IconChevronLeft size={16} />
                        </ActionIcon>
                        <Breadcrumbs separator={<IconChevronRight size={12} />} style={{ fontSize: '10px' }}>
                            {breadcrumbItems}
                        </Breadcrumbs>
                    </Group>
                )}

                <Title order={4}>{entity?.label || 'Loading...'}</Title>
                <Group>
                    <Badge color={entity?.zone === 'Upstream' ? 'blue' : 'orange'}>
                        {entity?.zone}
                    </Badge>
                    <Badge variant="outline" color="gray">{entity?.type}</Badge>
                </Group>

                <Divider my="sm" label="Triplets" labelPosition="center" />

                <ScrollArea h={400} offsetScrollbars>
                    <Table verticalSpacing="xs" style={{ fontSize: '12px' }}>
                        <Table.Tbody>
                            {triplets?.map((triplet, i) => (
                                <Table.Tr key={i}>
                                    <Table.Td fw={500} style={{ width: '40%' }}>{triplet.predicate.split(/[:#]/).pop()}</Table.Td>
                                    <Table.Td>
                                        {triplet.isUri ? (
                                            <Anchor size="xs" onClick={() => pushSelection(normalizeEntityId(triplet.object))}>
                                                {triplet.object}
                                            </Anchor>
                                        ) : (
                                            <Text size="xs">{triplet.object}</Text>
                                        )}
                                    </Table.Td>
                                </Table.Tr>
                            ))}
                            {(!triplets || triplets.length === 0) && (
                                <Table.Tr>
                                    <Table.Td colSpan={2}>
                                        <Text size="xs" c="dimmed" ta="center">No triplets found for this entity.</Text>
                                    </Table.Td>
                                </Table.Tr>
                            )}
                        </Table.Tbody>
                    </Table>
                </ScrollArea>

                <Divider my="sm" />

                <Text size="xs" fw={500}>URI:</Text>
                <Text size="xs" style={{ wordBreak: 'break-all' }} c="dimmed">
                    {entity?.id}
                </Text>
            </Stack>
        </Box>
    );
};

export default EntityDetails;
