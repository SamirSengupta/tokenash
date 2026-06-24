/**
 * Error hierarchy matching Python tokenash.exceptions.
 */

export class TokenashError extends Error {
  details?: Record<string, any>;

  constructor(message: string, details?: Record<string, any>) {
    super(message);
    this.name = "TokenashError";
    this.details = details;
  }
}

export class TokenashConnectionError extends TokenashError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, details);
    this.name = "TokenashConnectionError";
  }
}

export class TokenashAuthError extends TokenashError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, details);
    this.name = "TokenashAuthError";
  }
}

export class TokenashCompressError extends TokenashError {
  statusCode: number;
  errorType: string;

  constructor(statusCode: number, errorType: string, message: string, details?: Record<string, any>) {
    super(message, details);
    this.name = "TokenashCompressError";
    this.statusCode = statusCode;
    this.errorType = errorType;
  }
}

export class ConfigurationError extends TokenashError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, details);
    this.name = "ConfigurationError";
  }
}

export class ProviderError extends TokenashError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, details);
    this.name = "ProviderError";
  }
}

export class StorageError extends TokenashError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, details);
    this.name = "StorageError";
  }
}

export class TokenizationError extends TokenashError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, details);
    this.name = "TokenizationError";
  }
}

export class CacheError extends TokenashError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, details);
    this.name = "CacheError";
  }
}

export class ValidationError extends TokenashError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, details);
    this.name = "ValidationError";
  }
}

export class TransformError extends TokenashError {
  constructor(message: string, details?: Record<string, any>) {
    super(message, details);
    this.name = "TransformError";
  }
}

// --- Proxy error mapping ---

const ERROR_TYPE_MAP: Record<string, new (message: string, details?: Record<string, any>) => TokenashError> = {
  configuration_error: ConfigurationError,
  provider_error: ProviderError,
  storage_error: StorageError,
  tokenization_error: TokenizationError,
  cache_error: CacheError,
  validation_error: ValidationError,
  transform_error: TransformError,
};

/**
 * Map a proxy error response to the correct TokenashError subclass.
 */
export function mapProxyError(
  status: number,
  type: string,
  message: string,
): TokenashError {
  if (status === 401) return new TokenashAuthError(message);
  const ErrorClass = ERROR_TYPE_MAP[type];
  if (ErrorClass) return new ErrorClass(message, { statusCode: status, errorType: type });
  return new TokenashCompressError(status, type, message);
}
