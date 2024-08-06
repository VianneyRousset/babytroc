export default {
  hashingConfig: {
    // based on OWASP cheat sheet recommendations (as of March, 2022)
    parallelism: 1,
    memoryCost: 64000, // 64 mb
    timeCost: 3, // number of iterations
  },
}
