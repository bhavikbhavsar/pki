project(tks NONE)

add_subdirectory(src)
add_subdirectory(setup)
add_subdirectory(shared/conf)
add_subdirectory(${APP_SERVER})

# Create links at /usr/share/pki/tks/webapps/tks/admin/console.
# Create /usr/share/pki/tks/webapps/tks/WEB-INF/lib.
# This can be customized for different platforms in RPM spec.

add_custom_target(pki-tks-links ALL
    COMMENT "Creating links for TKS")

add_custom_command(
    TARGET pki-tks-links
    COMMAND ${CMAKE_COMMAND} -E make_directory webapp/admin
    COMMAND ln -sf ${DATA_INSTALL_DIR}/server/webapps/pki/admin/console ${CMAKE_CURRENT_BINARY_DIR}/webapp/admin
    COMMAND ${CMAKE_COMMAND} -E make_directory webapp/lib
    COMMAND ${CMAKE_COMMAND} -E create_symlink ${SLF4J_API_JAR} webapp/lib/slf4j-api.jar
    COMMAND ${CMAKE_COMMAND} -E create_symlink ${SLF4J_JDK14_JAR} webapp/lib/slf4j-jdk14.jar
    COMMAND ln -sf /usr/share/java/pki/pki-certsrv.jar ${CMAKE_CURRENT_BINARY_DIR}/webapp/lib/pki-certsrv.jar
    COMMAND ln -sf /usr/share/java/pki/pki-cms.jar ${CMAKE_CURRENT_BINARY_DIR}/webapp/lib/pki-cms.jar
    COMMAND ln -sf /usr/share/java/pki/pki-cmscore.jar ${CMAKE_CURRENT_BINARY_DIR}/webapp/lib/pki-cmscore.jar
    COMMAND ln -sf /usr/share/java/pki/pki-cmsbundle.jar ${CMAKE_CURRENT_BINARY_DIR}/webapp/lib/pki-cmsbundle.jar
    COMMAND ln -sf /usr/share/java/pki/pki-tks.jar ${CMAKE_CURRENT_BINARY_DIR}/webapp/lib/pki-tks.jar
)

# install directories
install(
    DIRECTORY
        shared/
    DESTINATION
        ${SHARE_INSTALL_PREFIX}/${APPLICATION_NAME}/${PROJECT_NAME}
    PATTERN
        "CMakeLists.txt" EXCLUDE
)

install(
    FILES
        ${CMAKE_CURRENT_BINARY_DIR}/webapp/admin/
    DESTINATION
        ${DATA_INSTALL_DIR}/tks/webapps/tks/admin
)

install(
    DIRECTORY
        ${CMAKE_CURRENT_BINARY_DIR}/webapp/lib/
    DESTINATION
        ${DATA_INSTALL_DIR}/tks/webapps/tks/WEB-INF/lib
)

# install empty directories
install(
    DIRECTORY
    DESTINATION
        ${VAR_INSTALL_DIR}/lock/pki/tks
)

install(
    DIRECTORY
    DESTINATION
        ${VAR_INSTALL_DIR}/run/pki/tks
)

