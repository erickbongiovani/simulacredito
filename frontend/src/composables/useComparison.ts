import { ref, readonly } from 'vue'
import { compareSimulations } from '../services/simulationService'
import type { ComparisonResponse, ComparisonRequest } from '../types/simulation'

export function useComparison() {
    const isLoading = ref(false)
    const error = ref<string | null>(null)
    const result = ref<ComparisonResponse | null>(null)

    async function runComparison(request: ComparisonRequest) {
        error.value = null
        result.value = null
        isLoading.value = true

        try {
            const response = await compareSimulations(request)
            result.value = response
        } catch (err) {
            error.value = (err as Error).message
        } finally {
            isLoading.value = false
        }
    }

    return {
        isLoading: readonly(isLoading),
        error: readonly(error),
        result: readonly(result),
        runComparison
    }
}
