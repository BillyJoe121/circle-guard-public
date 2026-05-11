FROM eclipse-temurin:21-jre
ARG JAR_FILE=build/libs/*SNAPSHOT.jar
WORKDIR /app
COPY ${JAR_FILE} app.jar
EXPOSE 8088
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
