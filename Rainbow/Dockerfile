FROM mcr.microsoft.com/dotnet/runtime:6.0 AS base
WORKDIR /app

FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /src
COPY ["Rainbow/Rainbow.csproj", "Rainbow/"]
RUN dotnet restore "Rainbow/Rainbow.csproj"
COPY . .
WORKDIR "/src/Rainbow"
RUN dotnet build "Rainbow.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "Rainbow.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "Rainbow.dll"]
