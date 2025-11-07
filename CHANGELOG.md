# Changelog

## [2.9.7](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.9.6...aegis-v2.9.7) (2025-11-07)


### Bug Fixes

* **bug:** inplacevar ([f8ce5bd](https://github.com/AEGIS-GAME/aegis/commit/f8ce5bdf611a21163e82d6bef27a2658746ef04f))
* **bug:** issue inplacevar ([9d645ce](https://github.com/AEGIS-GAME/aegis/commit/9d645ce941ca003595ae69c1ecfd093a1eb77709))
* **client:** Accidentally committed changes ([d1e2fa9](https://github.com/AEGIS-GAME/aegis/commit/d1e2fa955382e6c67dd959f1abe2759e2ae8ec7e))
* **client:** better text for console errors ([ab9ec3f](https://github.com/AEGIS-GAME/aegis/commit/ab9ec3f0ac70cde0c9e62cee404a7a7ebe3d4129))

## [2.9.6](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.9.5...aegis-v2.9.6) (2025-10-09)


### Bug Fixes

* **client:** info before toJSON on release workflow ([262f14c](https://github.com/AEGIS-GAME/aegis/commit/262f14c193aa18e335017e5e906ef8d6a48ebe73))
* **client:** revert ([4d6bb86](https://github.com/AEGIS-GAME/aegis/commit/4d6bb8656c03133682db857c6ef1641ec2de8728))

## [2.9.5](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.9.4...aegis-v2.9.5) (2025-10-04)


### Bug Fixes

* **packaging:** add missing package dep ([eed6b18](https://github.com/AEGIS-GAME/aegis/commit/eed6b18f334ee273cbccd6562642f989f9a35bec))

## [2.9.4](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.9.3...aegis-v2.9.4) (2025-10-04)


### Bug Fixes

* **client_installer:** fetch latest client from all releases ([#89](https://github.com/AEGIS-GAME/aegis/issues/89)) ([4b695e5](https://github.com/AEGIS-GAME/aegis/commit/4b695e5a8714f8066ccb9c41bdc904e9d025b8d7))
* **cooldown:** actually check cooldown so you can't spam commands ([#87](https://github.com/AEGIS-GAME/aegis/issues/87)) ([fd7cbb3](https://github.com/AEGIS-GAME/aegis/commit/fd7cbb3bc7373e612e4622bae8725c6ad479c086))

## [2.9.3](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.9.2...aegis-v2.9.3) (2025-10-03)


### Bug Fixes

* **cooldowns for scanning:** added cooldown to scan to make it like d… ([d382921](https://github.com/AEGIS-GAME/aegis/commit/d382921e2615aed80e4afccfb23db1de890d63c4))
* **cooldowns for scanning:** added cooldown to scan to make it like dig/save ([5e2f898](https://github.com/AEGIS-GAME/aegis/commit/5e2f8987b0b87aca491d98600bcd83fc676fcd71))

## [2.9.2](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.9.1...aegis-v2.9.2) (2025-10-03)


### Bug Fixes

* **surv file load bug:** remove proto bf survivor states to fix bug ([9123667](https://github.com/AEGIS-GAME/aegis/commit/91236672fb46a43843c6c52297f46114ae06ecc7))

## [2.9.1](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.9.0...aegis-v2.9.1) (2025-10-03)


### Bug Fixes

* layers revealed on either drone scan or adjacency (not both) ([cc6f948](https://github.com/AEGIS-GAME/aegis/commit/cc6f94873022b4bcb727ea7d548e1ea2043473aa))


### Documentation

* **contributing:** fix link ([#77](https://github.com/AEGIS-GAME/aegis/issues/77)) ([93235bb](https://github.com/AEGIS-GAME/aegis/commit/93235bb6bbd612e2b1e2d23d3c672f37edd25b91))

## [2.9.0](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.8.1...aegis-v2.9.0) (2025-09-16)


### Features

* **client:** updating client works i think ([0e3e6d9](https://github.com/AEGIS-GAME/aegis/commit/0e3e6d99776d6439f204458fbc90b2a4600c476a))


### Bug Fixes

* **aegis:** always remove prefix to version begfore writing/comparing ([37d4181](https://github.com/AEGIS-GAME/aegis/commit/37d4181378fba7d2b52d60e214a4c770629ba014))
* **updating:** remove debug, check for None ([de94e55](https://github.com/AEGIS-GAME/aegis/commit/de94e55907452ff8a3a9a6707ead9d1ba2f95c21))
* **updating:** some things ([efcc5d0](https://github.com/AEGIS-GAME/aegis/commit/efcc5d0a332167388942b8ffdd0e5ff7cc502a81))

## [2.8.1](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.8.0...aegis-v2.8.1) (2025-09-15)


### Bug Fixes

* add things ([425a407](https://github.com/AEGIS-GAME/aegis/commit/425a407464e62a06eefc8f03aabc418a01f0fe59))
* **aegis:** properly create client version file from aegis init ([cc6097d](https://github.com/AEGIS-GAME/aegis/commit/cc6097de9a3936fee9660b42c8edfa70ef673222))

## [2.8.0](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.7.6...aegis-v2.8.0) (2025-09-15)


### Features

* **client:** update client feature ([41963ac](https://github.com/AEGIS-GAME/aegis/commit/41963ac38061bdfd20b010933603e7a94a80a10e))


### Bug Fixes

* **aegis:** clean up client zip after installing ([a664e89](https://github.com/AEGIS-GAME/aegis/commit/a664e897831c6762f10e54b3a507cdc3e0d6c17e))
* client jsut checks version mismatch, aegis update just downloads ([85877fa](https://github.com/AEGIS-GAME/aegis/commit/85877fa7f45afe54710a6d071553e8604dc96967))
* using client-version.txt file for client version ([3fa68b1](https://github.com/AEGIS-GAME/aegis/commit/3fa68b1a468199095fc9571f15172c8c0c46f65e))


### Documentation

* **functions:** functions not following google style docstrings ([#61](https://github.com/AEGIS-GAME/aegis/issues/61)) ([2ee241b](https://github.com/AEGIS-GAME/aegis/commit/2ee241b120d738b742317ef033bd5a18c5a682fe))

## [2.7.6](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.7.5...aegis-v2.7.6) (2025-09-15)


### Bug Fixes

* **client win name:** . ([f753c2e](https://github.com/AEGIS-GAME/aegis/commit/f753c2e7860b99f1fce092401b57c2139441f8f0))

## [2.7.5](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.7.4...aegis-v2.7.5) (2025-09-14)


### Bug Fixes

* **permissions:** write perms ([1b9b956](https://github.com/AEGIS-GAME/aegis/commit/1b9b9563693f54bf4521e64535bf5d2c2d4513c6))

## [2.7.4](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.7.3...aegis-v2.7.4) (2025-09-14)


### Bug Fixes

* **release name:** . ([c1e0810](https://github.com/AEGIS-GAME/aegis/commit/c1e08103e627b6dc3d8bbb96a5622c464f67abee))

## [2.7.3](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.7.2...aegis-v2.7.3) (2025-09-14)


### Bug Fixes

* **just to force a aegis release:** . ([36a8b9c](https://github.com/AEGIS-GAME/aegis/commit/36a8b9cebef495eed3ce8f02b813ed2a95fda448))

## [2.7.2](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.7.1...aegis-v2.7.2) (2025-09-12)


### Bug Fixes

* **ci:** release wrong platforms ([ecbec71](https://github.com/AEGIS-GAME/aegis/commit/ecbec71816f5f2be925f38ef0fb60ef8a42bbc6c))

## [2.7.1](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.7.0...aegis-v2.7.1) (2025-09-12)


### Bug Fixes

* **workflows:** add missing steps ([4a24ef9](https://github.com/AEGIS-GAME/aegis/commit/4a24ef930a0fa86da488b1dbfcbde4c63feeabad))

## [2.7.0](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.6.4...aegis-v2.7.0) (2025-09-12)


### Features

* **new workflow:** move release into one workflow ([bf76e95](https://github.com/AEGIS-GAME/aegis/commit/bf76e95af4b9afdefd75a0a9cc1c09e1d29505da))

## [2.6.4](https://github.com/AEGIS-GAME/aegis/compare/aegis-v2.6.3...aegis-v2.6.4) (2025-09-12)


### Bug Fixes

* **tryign to force a release:** hate google ([#50](https://github.com/AEGIS-GAME/aegis/issues/50)) ([93179c4](https://github.com/AEGIS-GAME/aegis/commit/93179c4935cf98ee3b50197d0a60b034db0905fd))
