# AppleALC Layout Creation Workflow

## About

The processing workflow consists of six major phases, starting with obtaining and analyzing the audio codec data and ending with testing and optionally submitting the finished Layout-ID to the AppleALC repository.

The important aspect is that this is an iterative process: PinConfig, PathMap and Layout configuration may need to be adjusted repeatedly until the audio routing works correctly.

The diagram is designed as a high-level overview rather than a replacement for the detailed instructions in the individual chapters. It would fit well near the beginning of your README, immediately after the introduction and before the table of contents or preparation instructions.


## Workflow Diagram

### Phases

```mermaid
flowchart LR
    A["1. Preparation"] --> B["2. Codec Analysis"]
    B --> C["3. Layout Configuration"]
    C --> D["4. AppleALC Integration"]
    D --> E["5. Build & Testing"]
    E --> F["6. Finalization"]

    E -. "Test failed" .-> C
```

| Phase              | Main objective                                    | Primary output            |
| ------------------ | ------------------------------------------------- | ------------------------- |
| 1. Preparation     | Obtain and convert codec data                     | Codec dump and schematic  |
| 2. Analysis        | Identify nodes, signal paths and amp capabilities | Audio routing map         |
| 3. Configuration   | Create PinConfig, PathMap and Layout              | Three configuration files |
| 4. Integration     | Register all components in AppleALC               | Integrated source files   |
| 5. Build & Testing | Compile, install and validate                     | Working AppleALC.kext     |
| 6. Finalization    | Submit changes upstream (optional)                | AppleALC Pull Request (optional)   |

### Phases in Detail

```mermaid
flowchart TD
    Start(["Start: Create / Modify AppleALC Layout-ID"]) --> P1

    subgraph P1["1. Preparation & Extraction"]
        direction TB
        B["Boot Linux Live & Prepare Tools<br/><i>CodecGraph, PinConfigurator</i>"]
        C["Dump Codec & Convert<br/><code>codec-dump.txt</code> → <code>codec-dump_dec.txt</code>"]
        F["Generate Codec Schematic<br/><code>Codec-Dump.svg</code>"]
        B --> C --> F
    end

    subgraph P2["2. Codec Analysis"]
        direction TB
        G["Identify Codec & Vendor ID"]
        H["Analyze Pin Complex Nodes"]
        I["Trace I/O Paths, Mixers & Amps"]
        G --> H --> I
    end

    subgraph P3["3. Layout & Platform Config"]
        direction TB
        K["Pick Base Layout-ID & Select Unused ID"]
        M["Generate PinConfig<br/><i>PinConfigs.kext / info.plist</i>"]
        N["Create <code>PlatformsXX.xml</code><br/><i>Define PathMaps & Routing</i>"]
        O["Create <code>layoutXX.xml</code><br/><i>Define Codec, I/O & PathMapID</i>"]
        K --> M --> N --> O
    end

    subgraph P4["4. AppleALC Integration & Build"]
        direction TB
        Q["Merge PinConfigs into <code>PinConfigs.kext</code>"]
        R["Register Layout & Platforms in <code>info.plist</code>"]
        T["Compile AppleALC.kext<br/><code>xcodebuild -configuration Release</code>"]
        Q --> R --> T
    end

    subgraph P5["5. Testing & Verification"]
        direction TB
        U["Install Kext & Set Layout-ID in <code>config.plist</code>"]
        V["Reboot & Test Audio I/O"]
        W{"Audio Working<br/>as Expected?"}
        Fix["Adjust PinConfig, PathMap, or Layout"]
        U --> V --> W
        W -- "No" --> Fix
        Fix --> U
    end

    subgraph P6["6. Finalization"]
        direction TB
        X["Commit & Push to AppleALC Fork"]
        Z["Submit Pull Request"]
        AA(["Integrated upstream"])
        X --> Z --> AA
    end

    %% Phase Connections
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
    W -- "Yes" --> Fork{"Upstream<br/>Submission?"}
    Fork -- "Yes" --> P6
    Fork -- "No" --> Done(["Done: Local Layout-ID"])

    %% Clean Styling
    classDef terminal fill:#1e40af,stroke:#3b82f6,color:#fff,stroke-width:2px;
    classDef decision fill:#d97706,stroke:#f59e0b,color:#fff,stroke-width:2px;
    classDef success fill:#15803d,stroke:#22c55e,color:#fff,stroke-width:2px;

    class Start terminal;
    class W,Fork decision;
    class AA,Done success;
```

The following 3 aspects deserve particular attention in the diagram:

1. PinConfig and PathMap dependency: All nodes referenced in `PlatformsXX.xml` must also exist in the PinConfig. This makes their configuration interdependent.
2. Iterative troubleshooting: Testing is not simply the final step. Failed tests send you back to the configuration stage to adjust the PinConfig, PathMap or Layout.
3. Optional upstream contribution: A working custom Layout-ID does not necessarily have to be submitted to AppleALC. Pull Request submission is a separate final step.
