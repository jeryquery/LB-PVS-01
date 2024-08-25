FROM golang:latest

# Set destination for Copy
WORKDIR /app

# Download Go modules
COPY go.mod go.sum ./
RUN go mod download

# Copy the source code
COPY *.go ./

# Build
RUN CGO_ENABLED=0 GOOS=linux go build -o /docker-gs-ping

# Bind Port
EXPOSE 8080

# Run
CMD ["/docker-gs-ping"]