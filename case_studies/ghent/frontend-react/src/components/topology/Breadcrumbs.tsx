import React from 'react';
import { Breadcrumbs as MantineBreadcrumbs, Anchor, Text, Paper } from '@mantine/core';
import { useSelectionStore } from '../../stores/useSelectionStore';
import { useEntities } from '../../api/queries';

export const Breadcrumbs: React.FC = () => {
    const topologyHistory = useSelectionStore((state) => state.topologyHistory);
    const jumpToHistoryStep = useSelectionStore((state) => state.jumpToHistoryStep);
    const { data: entities } = useEntities();

    if (topologyHistory.length <= 1) return null;

    const items = topologyHistory.map((id, index) => {
        const entity = entities?.find((e) => e.id === id);
        const label = entity?.label || id.split('/').pop() || id;
        const isLast = index === topologyHistory.length - 1;

        if (isLast) {
            return (
                <Text key={id} size="sm" fw={500} c="dimmed">
                    {label}
                </Text>
            );
        }

        return (
            <Anchor
                key={id}
                component="button"
                size="sm"
                onClick={() => jumpToHistoryStep(index)}
                style={{ border: 'none', background: 'none', cursor: 'pointer', padding: 0 }}
            >
                {label}
            </Anchor>
        );
    });

    return (
        <Paper withBorder p="xs" mb="sm" shadow="xs" radius="md" style={{ backgroundColor: 'rgba(255, 255, 255, 0.8)', backdropFilter: 'blur(4px)' }}>
            <MantineBreadcrumbs separator="→" separatorMargin="md">
                {items}
            </MantineBreadcrumbs>
        </Paper>
    );
};
