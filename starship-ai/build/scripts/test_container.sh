process_container() {
    declare -i fail
    fail=0
    [[ -z "${BOLD_GREEN}" ]] && return $(error_exit "BOLD_GREEN not set - did you source tubs_funcs.sh?")
    [[ -z "${BOLD_RED}" ]] && return $(error_exit "BOLD_RED not set - did you source tubs_funcs.sh?")
    [[ -z "${NOCOLOR}" ]] && return $(error_exit "NOCOLOR not set - did you source tubs_funcs.sh?")
    [[ -z "${container}" ]] && return $(error_exit "container not set")
    [[ -z "${cn_ns}" ]] && return $(error_exit "cn_ns not set")
    [[ -z "${sub_version}" ]] && return $(error_exit "sub_version not set")
    [[ -z "${cic_repository}" ]] && return $(error_exit "cic_repository not set")

    test_container="${cn_ns}/${container}:${sub_version}"
    echo -e "        ${BOLD_GREEN}testing ${test_container}${NOCOLOR}"
    docker pull "${cic_repository}/${test_container}"
    docker tag "${cic_repository}/${test_container}" "${test_container}"
    set-container "${container}"-test.$$ "${container}:${sub_version}" "${cn_ns}"
    show-container
    sanity-test-container -s || fail=1
    ( check-command python3 --version ) || { echo -e "        ${BOLD_RED}ERROR: python3 command failed${NOCOLOR}" && fail=1 ; }
    ( check-command starship_ai --version ) || { echo -e "        ${BOLD_RED}ERROR: poc3 command failed${NOCOLOR}" && fail=1 ; }
    destroy-container
    show-container | grep 'No container found' > /dev/null || { echo -e "        ${BOLD_RED}ERROR: container not destroyed${NOCOLOR}" && fail=1 ; }
    docker rmi "${test_container}"
    [[ "${fail}" -eq 0 ]] && echo -e "        ${BOLD_GREEN}${test_container} atp${NOCOLOR}" || \
        echo -e "        ${BOLD_RED}${test_container} failed${NOCOLOR}"
    return $fail
}
