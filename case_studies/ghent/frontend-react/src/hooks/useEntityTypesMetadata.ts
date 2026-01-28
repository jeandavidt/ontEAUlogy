import { useMemo } from 'react';
import { useEntityTypes } from '../api/queries';
import type { EntityType } from '../api/types';

export const useEntityTypesMetadata = () => {
    const { data: entityTypes, isLoading, error } = useEntityTypes();

    const typeMetadata = useMemo(() => {
        if (!entityTypes) return {};

        const metadata = entityTypes.reduce((acc, entityType) => {
            acc[entityType.localName] = entityType;
            return acc;
        }, {} as Record<string, EntityType>);

        // Add reverse mappings for frontend types
        const reverseMappings: Record<string, string> = {
            'DWP': 'DrinkingWaterPlant',
            'WWTP': 'WastewaterTreatmentPlant',
            'Sensor': 'WaterSensor',
            'Industry': 'IndustrialFacility',
            'River': 'RiverSegment', // This might need adjustment
            'Residential': 'ResidentialDistrict',
        };

        Object.entries(reverseMappings).forEach(([frontendType, ontologyType]) => {
            if (metadata[ontologyType] && !metadata[frontendType]) {
                metadata[frontendType] = metadata[ontologyType];
            }
        });

        return metadata;
    }, [entityTypes]);

    const getDisplayLabel = (type: string): string => {
        return typeMetadata[type]?.displayLabel || type;
    };

    const getDisplayColor = (type: string): string => {
        return typeMetadata[type]?.displayColor || '#94a3b8'; // Default gray color
    };

    const getDisplayIcon = (type: string): string => {
        return typeMetadata[type]?.displayIcon || 'cube';
    };

    const getIconComponent = (type: string): string => {
        const icon = getDisplayIcon(type);
        
        // Map ontology icon names to Tabler icon components
        const iconMap: Record<string, string> = {
            'droplet-filled': 'IconDropletFilled',
            'building-factory': 'IconBuildingFactory2',
            'wave': 'IconRipple',
            'radar': 'IconBroadcast',
            'factory': 'IconBuildingFactory2',
            'home': 'IconHome',
            'network': 'IconNetwork',
            'cube': 'IconCube',
            'gear': 'IconSettings',
            'connection': 'IconPlug',
            'map': 'IconMap',
            'cpu': 'IconCpu',
            'radio-tower': 'IconBroadcast',
            'database': 'IconDatabase',
        };

        return iconMap[icon] || 'IconCube';
    };

    return {
        entityTypes,
        isLoading,
        error,
        typeMetadata,
        getDisplayLabel,
        getDisplayColor,
        getDisplayIcon,
        getIconComponent,
    };
};