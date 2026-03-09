import React from 'react';
import {
    BaseEdge,
    EdgeLabelRenderer,
    getSmoothStepPath,
    type EdgeProps,
} from 'reactflow';

export interface DataFlowEdgeData {
    parameterName: string;
}

const DataFlowEdge: React.FC<EdgeProps<DataFlowEdgeData>> = ({
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    data,
    animated,
}) => {
    const [edgePath, labelX, labelY] = getSmoothStepPath({
        sourceX,
        sourceY,
        sourcePosition,
        targetX,
        targetY,
        targetPosition,
    });

    return (
        <>
            <BaseEdge
                id={id}
                path={edgePath}
                style={{
                    stroke: '#228be6',
                    strokeWidth: 1.5,
                    strokeOpacity: 0.75,
                    strokeDasharray: animated ? '4 2' : undefined,
                }}
                markerEnd="url(#react-flow__arrowclosed)"
            />
            {data?.parameterName && (
                <EdgeLabelRenderer>
                    <div
                        style={{
                            position: 'absolute',
                            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
                            fontSize: 9,
                            background: 'rgba(255,255,255,0.92)',
                            border: '1px solid #dee2e6',
                            borderRadius: 4,
                            padding: '1px 5px',
                            color: '#495057',
                            pointerEvents: 'none',
                            whiteSpace: 'nowrap',
                        }}
                    >
                        {data.parameterName}
                    </div>
                </EdgeLabelRenderer>
            )}
        </>
    );
};

export default DataFlowEdge;
