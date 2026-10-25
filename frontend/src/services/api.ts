import axios from 'axios';
import type { AxiosInstance } from 'axios';
import { AxiosError } from 'axios';


const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const apiClient: AxiosInstance = axios.create({
    baseURL,
    headers: {
        'Content-Type': 'application/json'
    },
    timeout: 15000
});


function mensagemFormatada(error: AxiosError): string {
    //O servidor respondeu com algum código de erro HTTP (4xx, 5xx)
    if(error.response) {
        const status = error.response.status;
        const data = error.response.data as any;
        
        //Se for erro de validação do Pydantic (422)
        if(status === 422 && Array.isArray(data?.detail)){
            const primeiro = data.detail[0];
            return `Dado invalido no campo "${primeiro?.loc?.slice(-1)}": ${primeiro?.msg}`;
        }

        if (status >= 500) {
            return 'Erro interno do servidor';
        }

        return data?.detail ||'Erro desconhecido no servidor';
    }

    //A requisição foi enviada, mas não houve resposta (servidor desligado / timeout)
    if (error.request){
        return 'Erro de conexão com a API de simulações';
    }

    return 'Erro na configuração de requisição';
}


apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error: AxiosError) => {
        return Promise.reject(new Error(mensagemFormatada(error)
        ));
    }
);