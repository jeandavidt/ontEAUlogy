import React from 'react';
import { type NodeProps } from 'reactflow';
import { Text } from '@mantine/core';

export interface LayerGroupNodeData {
    label: string;
    color: string;
}

const LayerGroupNode: React.FC<NodeProps<LayerGroupNodeData>> = ({ data, style }) => {
    return (
        <div
            style={{
                ...style,
                backgroundColor: data.color,
                border: '1px solid rgba(0,0,0,0.08)',
                borderRadius: 8,
                padding: '8px 10px',
                width: '100%',
                height: '100%',
                boxSizing: 'border-box',
                pointerEvents: 'none',
            }}
        >
            <Text
                size="xs"
                fw={600}
                c="dimmed"
                style={{ userSelect: 'none', pointerEvents: 'none' }}
            >
                {data.label}
            </Text>
        </div>
    );
};

export default LayerGroupNode;
