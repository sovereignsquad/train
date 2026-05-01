import Foundation

enum APIClientError: Error, LocalizedError {
    case invalidResponse
    case requestFailed(Int, String)
    case missingBaseURL

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "The API returned an invalid response."
        case .requestFailed(let status, let body):
            return "The API request failed with \(status): \(body)"
        case .missingBaseURL:
            return "The engine base URL is not configured."
        }
    }
}

struct APIClient {
    let baseURL: URL

    func get<T: Decodable>(_ path: String, as type: T.Type) async throws -> T {
        let request = URLRequest(url: endpoint(path))
        let (data, response) = try await URLSession.shared.data(for: request)
        return try decode(data: data, response: response, as: type)
    }

    func post<Body: Encodable, T: Decodable>(_ path: String, body: Body, as type: T.Type) async throws -> T {
        var request = URLRequest(url: endpoint(path))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)
        let (data, response) = try await URLSession.shared.data(for: request)
        return try decode(data: data, response: response, as: type)
    }

    func post<T: Decodable>(_ path: String, as type: T.Type) async throws -> T {
        var request = URLRequest(url: endpoint(path))
        request.httpMethod = "POST"
        let (data, response) = try await URLSession.shared.data(for: request)
        return try decode(data: data, response: response, as: type)
    }

    func put<Body: Encodable, T: Decodable>(_ path: String, body: Body, as type: T.Type) async throws -> T {
        var request = URLRequest(url: endpoint(path))
        request.httpMethod = "PUT"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)
        let (data, response) = try await URLSession.shared.data(for: request)
        return try decode(data: data, response: response, as: type)
    }

    func delete(_ path: String) async throws {
        var request = URLRequest(url: endpoint(path))
        request.httpMethod = "DELETE"
        let (_, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw APIClientError.invalidResponse
        }
        guard (200...299).contains(http.statusCode) else {
            throw APIClientError.requestFailed(http.statusCode, "")
        }
    }

    private func endpoint(_ path: String) -> URL {
        baseURL.appendingPathComponent(path.trimmingCharacters(in: CharacterSet(charactersIn: "/")))
    }

    private func decode<T: Decodable>(data: Data, response: URLResponse, as type: T.Type) throws -> T {
        guard let http = response as? HTTPURLResponse else {
            throw APIClientError.invalidResponse
        }
        guard (200...299).contains(http.statusCode) else {
            let body = String(data: data, encoding: .utf8) ?? ""
            throw APIClientError.requestFailed(http.statusCode, body)
        }
        return try JSONDecoder().decode(type, from: data)
    }
}
