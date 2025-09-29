class BatchCaller:
    def __init__(
        self,
        provider: Provider,
        *,
        concurrency: int = 8,
        qps: float | None = None,
        timeout: float | None = 60.0,
        retry: RetryStrategy | None = None,
        transport: AsyncTransport | None = None,
        hooks: Hooks | None = None,           # on_start/on_success/on_error
    ): ...

    async def generate(
        self,
        request: Request,
        *,
        validate: ValidationHook | None = None,
        timeout: float | None = None
    ) -> Response: ...

    async def batch(
        self,
        requests: Sequence[Request],
        *,
        validate: ValidationHook | None = None,
        return_exceptions: bool = False
    ) -> list[Response | Exception]: ...

    async def stream(
        self,
        request: Request,
        *,
        timeout: float | None = None
    ) -> AsyncIterator[ResponseChunk]: ...

    async def aclose(self) -> None: ...
    async def __aenter__(self) -> "BatchAI": ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...
