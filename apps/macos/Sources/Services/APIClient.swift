import Foundation

enum APIClientError: Error, LocalizedError {
    case invalidResponse
    case requestFailed(Int, String)
    case missingBaseURL
    case transportFailed(String)
    case decodingFailed(String)

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "The API returned an invalid response."
        case .requestFailed(let status, let body):
            let trimmedBody = body.trimmingCharacters(in: .whitespacesAndNewlines)
            if trimmedBody.isEmpty {
                return "The API request failed with status \(status)."
            }
            return "The API request failed with status \(status): \(trimmedBody)"
        case .missingBaseURL:
            return "The engine base URL is not configured."
        case .transportFailed(let detail):
            return detail
        case .decodingFailed(let detail):
            return detail
        }
    }
}

struct APIClient {
    let baseURL: URL

    func get<T: Decodable>(_ path: String, as type: T.Type) async throws -> T {
        let request = URLRequest(url: endpoint(path))
        let (data, response) = try await perform(request)
        return try decode(data: data, response: response, as: type)
    }

    func post<Body: Encodable, T: Decodable>(_ path: String, body: Body, as type: T.Type) async throws -> T {
        var request = URLRequest(url: endpoint(path))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)
        let (data, response) = try await perform(request)
        return try decode(data: data, response: response, as: type)
    }

    func post<T: Decodable>(_ path: String, as type: T.Type) async throws -> T {
        var request = URLRequest(url: endpoint(path))
        request.httpMethod = "POST"
        let (data, response) = try await perform(request)
        return try decode(data: data, response: response, as: type)
    }

    func put<Body: Encodable, T: Decodable>(_ path: String, body: Body, as type: T.Type) async throws -> T {
        var request = URLRequest(url: endpoint(path))
        request.httpMethod = "PUT"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)
        let (data, response) = try await perform(request)
        return try decode(data: data, response: response, as: type)
    }

    func delete(_ path: String) async throws {
        var request = URLRequest(url: endpoint(path))
        request.httpMethod = "DELETE"
        let (_, response) = try await perform(request)
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

    private func perform(_ request: URLRequest) async throws -> (Data, URLResponse) {
        do {
            return try await URLSession.shared.data(for: request)
        } catch let error as URLError {
            throw APIClientError.transportFailed(Self.message(for: error))
        } catch {
            throw APIClientError.transportFailed(error.localizedDescription)
        }
    }

    private func decode<T: Decodable>(data: Data, response: URLResponse, as type: T.Type) throws -> T {
        guard let http = response as? HTTPURLResponse else {
            throw APIClientError.invalidResponse
        }
        guard (200...299).contains(http.statusCode) else {
            let body = String(data: data, encoding: .utf8) ?? ""
            throw APIClientError.requestFailed(http.statusCode, body)
        }
        do {
            return try JSONDecoder().decode(type, from: data)
        } catch {
            throw APIClientError.decodingFailed(
                "The engine response could not be decoded. Check the local API version and retry."
            )
        }
    }

    static func message(for error: Error) -> String {
        if let apiError = error as? APIClientError {
            return apiError.localizedDescription
        }
        if let urlError = error as? URLError {
            return message(for: urlError)
        }
        return error.localizedDescription
    }

    private static func message(for error: URLError) -> String {
        switch error.code {
        case .timedOut:
            return "The local engine did not respond in time."
        case .cannotConnectToHost, .cannotFindHost, .networkConnectionLost, .notConnectedToInternet:
            return "The local engine is temporarily unreachable."
        case .badServerResponse:
            return "The local engine returned an invalid response."
        default:
            return error.localizedDescription
        }
    }
}
