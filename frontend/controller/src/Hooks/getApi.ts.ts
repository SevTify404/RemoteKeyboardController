export interface IpResponse {
    ip_address: string | null;
}

//logique de recupertation de l'id par la backend automatiqquement 
export async function fetchBackendIP(): Promise<string> {
    try {
        const response = await fetch('http://127.0.0.1:8000/utils/get-lan-ip');

        if (response.ok) {
            const data: IpResponse = await response.json();
            if (data.ip_address) {
                console.log(`IP récupérée du backend: ${data.ip_address}`);
                return data.ip_address;
            }
        }
    } catch (error) {
        console.warn(' Échec de récupération de l\'IP depuis le backend:', error);
    }

    
    console.log('Utilisation du fallback: 127.0.0.1');
    return '127.0.0.1';
}
