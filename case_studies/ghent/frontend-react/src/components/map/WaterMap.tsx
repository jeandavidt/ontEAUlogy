import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useEntities, useRelationships } from '../../api/queries';
import { useSelectionStore } from '../../stores/useSelectionStore';
import { useEntityTypesMetadata } from '../../hooks/useEntityTypesMetadata';
import L from 'leaflet';
import type { LatLngExpression } from 'leaflet';
import { renderToStaticMarkup } from 'react-dom/server';
import {
    IconRipple,
    IconDropletFilled,
    IconRecycle,
    IconBuildingFactory2,
    IconHome,
    IconBroadcast,
    IconCube,
    IconNetwork,
    IconSettings,
    IconPlug,
    IconMap,
    IconCpu,
    IconDatabase
} from '@tabler/icons-react';

const GHENT_CENTER: LatLngExpression = [51.056, 3.722];

const getDynamicIcon = (color: string, iconName: string) => {
    const iconComponents: Record<string, React.ElementType> = {
        IconRipple,
        IconDropletFilled,
        IconRecycle,
        IconBuildingFactory2,
        IconHome,
        IconBroadcast,
        IconCube,
        IconNetwork,
        IconSettings,
        IconPlug,
        IconMap,
        IconCpu,
        IconDatabase,
    };

    const IconComp = iconComponents[iconName] || IconCube;

    const html = renderToStaticMarkup(
        <div style={{
            color: color,
            backgroundColor: 'white',
            borderRadius: '50%',
            padding: '4px',
            border: `2px solid ${color}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
        }}>
            <IconComp size={20} />
        </div>
    );

    return L.divIcon({
        html,
        className: 'custom-div-icon',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
    });
};

const WaterMap: React.FC = () => {
    const { data: entities, isLoading: entitiesLoading } = useEntities();
    const { data: relationships, isLoading: relsLoading } = useRelationships();
    const { getDisplayColor, getIconComponent } = useEntityTypesMetadata();
    const setSelectedEntityId = useSelectionStore((state) => state.setSelectedEntityId);

    if (entitiesLoading || relsLoading) return <div>Loading Map...</div>;

    // Filter relationships to only those where both entities exist on map
    const mapConnections = relationships?.map(rel => {
        const source = entities?.find(e => e.id === rel.source);
        const target = entities?.find(e => e.id === rel.target);
        if (source && target) {
            return {
                path: [source.coordinates, target.coordinates] as LatLngExpression[],
                label: rel.label,
                source: source.label,
                target: target.label,
                predicate: rel.predicate
            };
        }
        return null;
    }).filter(Boolean);

    return (
        <MapContainer center={GHENT_CENTER} zoom={13} style={{ height: '100%', width: '100%' }}>
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* Draw Relationships */}
            {mapConnections?.map((conn, i) => (
                <Polyline
                    key={i}
                    positions={conn!.path}
                    color="#868e96"
                    weight={2}
                    opacity={0.6}
                    dashArray="5, 10"
                >
                    <Tooltip sticky>
                        <div style={{ fontSize: '11px' }}>
                            <strong>{conn!.label}</strong><br />
                            {conn!.source} &rarr; {conn!.target}
                        </div>
                    </Tooltip>
                </Polyline>
            ))}

            {/* Draw Markers */}
            {entities?.filter((entity) => {
                const [lat, lon] = entity.coordinates;
                return lat > 0 && lon > 0; // Filter out entities with invalid coordinates
            }).map((entity) => {
                const color = getDisplayColor(entity.type);
                const iconName = getIconComponent(entity.type);
                
                return (
                    <Marker
                        key={`${entity.id}-${entity.uri}`}
                        position={entity.coordinates as LatLngExpression}
                        icon={getDynamicIcon(color, iconName)}
                        eventHandlers={{
                            click: () => setSelectedEntityId(entity.id),
                        }}
                    >
                        <Popup>
                            <strong>{entity.label}</strong>
                            <br />
                            Type: {entity.type}
                            <br />
                            Zone: {entity.zone}
                        </Popup>
                    </Marker>
                );
            })}
        </MapContainer>
    );
};

export default WaterMap;
