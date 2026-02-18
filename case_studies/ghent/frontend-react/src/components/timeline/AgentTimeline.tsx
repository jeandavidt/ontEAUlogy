import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import type { TraceGraph } from '../../api/traceTypes';

interface AgentTimelineProps {
    traceGraph: TraceGraph;
    onNodeClick: (nodeId: string) => void;
    selectedNodeId?: string;
}

const agentColors: Record<string, string> = {
    orchestrator: '#6366f1',
    sparql: '#8b5cf6',
    simulation: '#10b981',
    optimization: '#f59e0b',
    composition: '#ec4899',
    llm: '#3b82f6',
};

export const AgentTimeline: React.FC<AgentTimelineProps> = ({
    traceGraph,
    onNodeClick,
    selectedNodeId,
}) => {
    const svgRef = useRef<SVGSVGElement>(null);

    useEffect(() => {
        if (!svgRef.current || !traceGraph.nodes.length) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();

        const width = 900;
        const height = 400;
        const margin = { top: 40, right: 40, bottom: 40, left: 40 };

        const g = svg
            .attr('width', width)
            .attr('height', height)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        const nodes = traceGraph.nodes.map(n => ({ ...n }));
        const links = traceGraph.links.map(l => ({
            source: l.source,
            target: l.target,
        }));

        const nodeMap = new Map(nodes.map(n => [n.id, n]));

        const treeLayout = d3.tree<typeof nodes[0]>()
            .size([innerWidth, innerHeight - 50])
            .separation((a, b) => (a.parent === b.parent ? 1 : 1.5));

        const root = d3.hierarchy(nodes[0], d => {
            const children: typeof nodes[0][] = [];
            links.forEach(l => {
                if (l.source === d.id) {
                    const child = nodeMap.get(l.target);
                    if (child) children.push(child);
                }
            });
            return children.length ? { children } : null;
        });

        const treeData = treeLayout(root);

        g.selectAll('.link')
            .data(treeData.links())
            .join('path')
            .attr('class', 'link')
            .attr('fill', 'none')
            .attr('stroke', '#94a3b8')
            .attr('stroke-width', 2)
            .attr('d', d3.linkVertical<d3.HierarchyPointLink<typeof nodes[0]>, d3.HierarchyPointNode<typeof nodes[0]>>()
                .x(d => d.x)
                .y(d => d.y)
            );

        const nodeGroups = g.selectAll('.node')
            .data(treeData.descendants())
            .join('g')
            .attr('class', 'node')
            .attr('transform', d => `translate(${d.x},${d.y})`)
            .style('cursor', 'pointer')
            .on('click', (_, d) => onNodeClick(d.data.id));

        nodeGroups.append('circle')
            .attr('r', 20)
            .attr('fill', d => agentColors[d.data.agent_type] || '#94a3b8')
            .attr('stroke', d => d.data.id === selectedNodeId ? '#000' : '#fff')
            .attr('stroke-width', d => d.data.id === selectedNodeId ? 3 : 2);

        nodeGroups.append('text')
            .attr('dy', 35)
            .attr('text-anchor', 'middle')
            .attr('font-size', '11px')
            .attr('fill', '#475569')
            .text(d => d.data.agent_id);

        nodeGroups.append('text')
            .attr('dy', -25)
            .attr('text-anchor', 'middle')
            .attr('font-size', '9px')
            .attr('fill', '#64748b')
            .text(d => d.data.agent_type);

    }, [traceGraph, selectedNodeId, onNodeClick]);

    return (
        <svg ref={svgRef} style={{ width: '100%', maxWidth: 900 }} />
    );
};
