import { ref, readonly } from 'vue'
import { calculateSimulation } from '../services/simulationService'
import type { SimulationResponse, SimulationRequest } from '../types/simulation'


export function useSimulation() {
    const isLoading = ref(false);
    const error = ref<string | null>(null);
    const result = ref<SimulationResponse | null>(null)

    async function runSimulation(request: SimulationRequest) {
        error.value = null;
        result.value = null;
        isLoading.value = true;

        try {
            const response = await calculateSimulation(request);
            result.value = response;
        } catch (err) {
            error.value = (err as Error).message
        } finally {
            isLoading.value = false;
        }

    }

    return {
        isLoading: readonly(isLoading),
        error: readonly(error),
        result: readonly(result),
        runSimulation
    }
}