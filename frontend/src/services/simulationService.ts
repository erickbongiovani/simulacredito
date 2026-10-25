import type {SimulationRequest, SimulationResponse, ComparisonRequest, ComparisonResponse } from '../types/simulation'
import { apiClient } from './api'




export async function calculateSimulation(data: SimulationRequest): Promise<SimulationResponse> {
    try {
        const response = await apiClient.post<SimulationResponse>('/simulations/calculate', data);
        return response.data;
    } catch (error) {
        throw error;
    }
}

export async function compareSimulations(data: ComparisonRequest): Promise<ComparisonResponse> {
    try {
        const response = await apiClient.post<ComparisonResponse>('/simulations/compare', data)
        return response.data;    
    } catch (error) {
        throw error;
    }
}

