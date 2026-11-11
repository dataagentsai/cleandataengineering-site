SERVICE = {
    "slug": "iot-greengrass",
    "name": "AWS IoT Greengrass",
    "short": "IoT Greengrass",
    "group": "ingestion",
    "one_line": "An edge runtime on a plant gateway that runs collectors, buffers data when offline and exports it to Kinesis, deployed from the cloud.",
    "status": "Version 2 generally available. Version 1 reached end of support on 7 Oct 2026; its APIs and resources are no longer available, so v1 devices must move to v2.",
    "checked": "2026-11-11",
    "site_verdict": ("Pursue",
                     "The runtime on each plant gateway: it hosts SiteWise Edge to read OPC UA and Modbus machines, buffers to local disk "
                     "when the line to AWS drops, and its stream manager exports batches straight to Kinesis using the token exchange "
                     "role, so plant data skips per-message IoT Core charges."),
    "equivalents": {"azure": "Azure IoT Edge (and Azure IoT Operations)",
                    "gcp": "none native; partner edge platforms or a self-run container host",
                    "databricks": "none: Databricks reads what the gateway sends to Kinesis or S3",
                    "open_source": "Eclipse Kura, or K3s plus your own containers; Greengrass nucleus itself is open source"},
    "plain": [
        "AWS IoT Greengrass is software you install on a small computer that sits next to your machines, called an edge device or "
        "gateway. It might be an industrial PC in a cabinet on the factory floor, or a box in the back room of a retail shop. "
        "Greengrass turns that box into something you can manage from AWS: you package code as components, and AWS deploys, starts, "
        "restarts and updates them on hundreds of gateways at once. Without it you would log in to each box to copy files and restart "
        "services by hand.",
        "The core piece is the nucleus, a small runtime that talks to AWS, receives deployments and runs your components. There are "
        "two kinds. The standard nucleus is written in Java and supports every feature. Nucleus lite is written in C, needs less than "
        "15 MB of memory, and is meant for small Linux devices; it supports a subset of features, so check the AWS compatibility "
        "table before choosing it. AWS also ships ready-made components, such as stream manager, which buffers data on local disk and "
        "exports it in batches to Kinesis Data Streams, S3 or IoT SiteWise.",
        "A concrete example: a tyre plant has forty curing presses and twelve mixers. Each speaks OPC UA, a standard industrial "
        "protocol for reading machine values such as temperature, pressure and cycle time. One industrial PC per plant runs "
        "Greengrass with the IoT SiteWise Edge components. The SiteWise collector reads about two thousand values a second from the "
        "machines, and stream manager sends them to a Kinesis stream in batches of up to 500 records. If the plant's internet line "
        "goes down for an hour, the readings wait on the gateway's disk and are sent when the line returns.",
    ],
    "analogy": "A site foreman's office at each plant that AWS can staff and re-equip remotely, with a storeroom that holds shipments when the road is closed.",
    "big_picture": [
        "On the reference platform Greengrass is the runtime on every plant gateway, at the start of the move-in lane for sensor data. "
        "It hosts SiteWise Edge, which talks to the presses and mixers, and stream manager, which exports to Kinesis Data Streams in "
        "the cloud. The gateway gets temporary AWS credentials through the token exchange role, so it writes to Kinesis with IAM, "
        "not through the IoT Core message broker. This is the path the site's streaming design calls the gateway writing directly to "
        "Kinesis, and it saves roughly a thousand dollars a month compared with sending every reading through IoT Core.",
        "The site deliberately skips SiteWise cloud storage and asset modelling for analytics, which is priced per data point; the "
        "gateway sends raw readings to Kinesis, and Databricks builds the bronze, silver and gold tables. Machine alarms and safety "
        "interlocks stay on the plant floor with the machines' own controls; the platform is for analysis, not for stopping a press.",
        "Greengrass still relies on IoT Core for the control side: each gateway is a registered thing with its own certificate, and "
        "deployments arrive through IoT Core. When control is in scope, Greengrass deployments are also how you change gateway "
        "settings, such as which machine tags to read. CloudWatch receives the gateway's health telemetry and logs.",
    ],
    "upstream": ["Curing presses and mixers (OPC UA, Modbus)", "Plant historian", "Shop-floor PLCs and sensors"],
    "downstream": ["svc:kinesis-data-streams", "svc:iot-sitewise", "svc:s3"],
    "concepts": [
        ("Core device", "A gateway or edge computer running the Greengrass Core software. It is registered in AWS as an IoT thing with its own certificate."),
        ("Nucleus", "The runtime that receives deployments and runs components. The standard nucleus uses Java; nucleus lite is a small C runtime for constrained Linux devices."),
        ("Component", "A package of software with a recipe (what to install and run) and artifacts (the files). It can be a script, a binary, a Docker container or a Lambda function."),
        ("Deployment", "A cloud-side instruction that sends a set of components and their configuration to one device or a thing group."),
        ("Thing group", "A named group of devices, such as all gateways in one plant, so one deployment updates them together."),
        ("Stream manager", "An AWS component that stores data streams on local disk and exports them in batches to Kinesis, S3 or SiteWise, retrying after outages."),
        ("Token exchange role", "An IAM role the device assumes through an IoT role alias, giving components short-lived AWS credentials instead of stored keys."),
        ("SiteWise Edge", "AWS IoT SiteWise components that run on Greengrass, collect values from OPC UA and Modbus machines and can process them locally."),
        ("Local deployment", "Installing or testing components directly on the device with the command line, without a cloud deployment."),
    ],
    "use_when": [
        "You need a gateway inside a plant or shop that collects machine data and sends it to AWS, and you have more than a handful of sites to manage.",
        "The site's network is unreliable and data must wait on local disk and be sent later without loss.",
        "You want to deploy and update gateway software from the cloud to a group of devices instead of logging in to each one.",
        "You use IoT SiteWise Edge collectors for OPC UA or Modbus machines, which run as Greengrass components.",
        "You want gateway code to call AWS with short-lived IAM credentials rather than access keys stored on the box.",
    ],
    "avoid_when": [
        "The plant already runs a mature industrial platform, such as Kepware or Ignition, that can publish to Kinesis or MQTT; the site keeps that rather than adding Greengrass.",
        "You only have one or two simple devices that can call AWS directly; a full edge runtime adds work you do not need.",
        "You need hard real-time control or safety functions; those belong in the machine controllers, not in a Linux gateway.",
        "Your gateways run an operating system Greengrass does not support, or have too little memory for the standard nucleus and the features you need are missing from nucleus lite.",
    ],
    "challenges": [
        ("Still on version 1",
         "Greengrass v1 reached end of support on 7 Oct 2026 and its APIs are gone, so v1 gateways can no longer be managed from the cloud.",
         "Move each gateway to v2 using the AWS migration guide; repackage v1 Lambda functions as v2 components and test on one plant first."),
        ("Disk fills during a long outage",
         "Stream manager buffers to local disk; if the line is down for a day, the buffer reaches its limit and the oldest data is dropped or new data rejected.",
         "Size the gateway disk for your longest expected outage, set the stream's maximum size and overflow strategy on purpose, and alarm on stream backlog."),
        ("Kinesis throttling from the gateway",
         "Stream manager sends faster than the shards accept, so exports retry and the backlog grows.",
         "Use stream manager 2.3.1 or later with shard-aware pacing, which needs kinesis:ListShards in the token exchange role; or put the stream in on-demand mode."),
        ("Over-broad token exchange role",
         "The default role examples grant wide S3 or Kinesis access, so a compromised gateway can read or write far more than its own stream.",
         "Scope the role to the one Kinesis stream and the artifact bucket each plant needs, with one role alias per plant if plants must be isolated."),
        ("Bad deployment to every plant",
         "A component update with a bug goes to all gateways at once and stops data collection everywhere.",
         "Deploy to one thing group per plant, start with a pilot plant, use rollback on failure, and keep component versions pinned."),
        ("Gateway goes quiet without anyone noticing",
         "The gateway is powered off or loses its certificate, and the platform sees only that data stopped.",
         "Turn on the telemetry and log components, alarm on core device health status, and keep the site's per-plant heartbeat check on the Kinesis stream."),
        ("Clock drift on the gateway",
         "Readings are stamped with a wrong time, so windows and joins in silver are off.",
         "Run time synchronisation on the gateway, and store both the device time and the Kinesis arrival time in bronze."),
    ],
    "compare": [
        ("Third-party industrial software (Kepware, Ignition)",
         "The plant already runs it and its team knows it; the site rates this Pursue if present.",
         "You are starting fresh and want one AWS-managed runtime for collection, buffering and deployment."),
        ("Our own Python service on a small box",
         "Never for production; the site drops it.",
         "Always: you would own buffering, retries, updates and security patches yourself."),
        ("Devices sending through AWS IoT Core directly",
         "Each device needs its own identity and commands back, as with connected tyres.",
         "Machines sit behind one gateway in a plant; that path adds per-message charges."),
        ("Azure IoT Edge or Azure IoT Operations",
         "The platform is on Azure; the ideas of modules, deployments and edge buffering are the same.",
         "You are on AWS; staying with Greengrass keeps identity and deployments in one place."),
        ("K3s or Docker on the gateway, managed by your own tooling",
         "You already run a fleet of edge Kubernetes clusters and have a team for it.",
         "You want AWS to handle deployments, credentials and the export component for you."),
    ],
    "cost": {
        "model": "Greengrass is charged per active core device per month. A core counts as active in any month it authenticates with AWS; "
                 "the AWS pricing examples use about sixteen cents per device per month, list price, check your region. The first "
                 "three core devices are free each month for the first year. The fee itself is small. The real costs sit around it: "
                 "IoT Core connection minutes and any MQTT messages the device sends, Kinesis shard hours and payload units, "
                 "CloudWatch logs and metrics from the gateway, and the gateway hardware, which is not an AWS charge at all.",
        "drivers": [
            "The number of gateways that authenticate each month, which is usually one or two per plant.",
            "Which path the data takes: stream manager to Kinesis costs only Kinesis, while publishing through IoT Core adds per-message and rule charges.",
            "How verbose the gateway logs are when sent to CloudWatch Logs.",
            "SiteWise cloud features, if used, which are priced per data point and asset rather than per device.",
        ],
        "traps": [
            "Decommissioned gateways that still authenticate keep being billed; stop the nucleus and delete the core device to stop the charge.",
            "Sending gateway data through IoT Core messages instead of stream manager to Kinesis, adding about a thousand dollars a month in the site's estimate.",
            "Turning on SiteWise cloud storage and asset models for all tags when the analytics happen in Databricks anyway.",
            "Debug-level component logs uploaded to CloudWatch from every plant.",
        ],
    },
    "security": [
        "Each gateway has its own X.509 certificate; keep the private key in a TPM or hardware security module where possible, which both nuclei support.",
        "Components get AWS access only through the token exchange role; scope it to the gateway's own Kinesis stream and artifact bucket, and never store access keys on the box.",
        "Put the gateway on the plant's operations network segment with outbound-only access on port 443 or 8883 to AWS IoT endpoints; no inbound ports from the internet.",
        "Run components as a non-root system user, configured through the nucleus run-with-default setting.",
        "CloudTrail records every deployment and change to components and role aliases; review who can create deployments, because that is code execution on every plant.",
        "Machine readings are rarely personal data, but operator badge IDs or shift logs on the same gateway are; keep them out of the sensor stream or tokenise them in the lander.",
    ],
    "monitor": [
        ("Core device health status", "Whether each gateway reports HEALTHY or UNHEALTHY to the Greengrass service; alarm when a plant's gateway turns unhealthy."),
        ("Deployment status", "Whether the latest deployment to each thing group succeeded, failed or rolled back."),
        ("Stream manager backlog", "How much data waits on the gateway's disk for export; a growing number means Kinesis throttling or a network outage."),
        ("System telemetry (CPU, memory, disk)", "Gateway resource use from the nucleus telemetry, so a full disk is found before data is lost."),
        ("Kinesis IncomingRecords per plant", "A cloud-side heartbeat: if records from one plant stop, the gateway or its network is down."),
        ("Greengrass component logs in CloudWatch Logs", "Errors from the SiteWise collector and stream manager, such as lost OPC UA connections."),
    ],
    "limits": [
        ("Component recipe size", "16 KB per recipe"),
        ("Total artifact size per component", "2 GB"),
        ("Components per Region", "5,000"),
        ("Thing group deployment document", "31 KB without large configuration support, 6 MB with it"),
        ("Nucleus lite footprint", "Less than 15 MB of RAM and about 5 MB of storage for the runtime"),
    ],
    "decisions": [
        ("Forty presses and twelve mixers in one plant, 2,000 readings a second", "Greengrass gateway with SiteWise Edge and stream manager exporting to Kinesis",
         "Pursue: the site's chosen path; built-in collectors, offline buffering and no per-message charges."),
        ("A plant that already runs Ignition with an MQTT or Kinesis module", "Keep Ignition publishing to Kinesis",
         "Keep if you have it: do not add Greengrass where a mature industrial platform already does the job."),
        ("Gateways still on Greengrass v1", "Migrate to v2 now",
         "Drop: v1 reached end of support on 7 Oct 2026 and can no longer be managed."),
        ("Small sensor boxes with 64 MB of memory in retail shops", "Nucleus lite with a minimal component set",
         "Pursue with care: check that every feature you need is listed as supported for nucleus lite."),
    ],
    "faq": [
        ("Is AWS IoT Greengrass v1 still supported?",
         "No. AWS ended support for Greengrass v1 on 7 October 2026, and the v1 API operations and resources are no longer available. Devices must be migrated to version 2."),
        ("What is Greengrass nucleus lite?",
         "A small C runtime for constrained Linux devices, using less than 15 MB of RAM. It runs Greengrass generic components and a subset of the v2 features, and can be mixed in one fleet with the standard Java nucleus."),
        ("How does Greengrass send data to Kinesis?",
         "The stream manager component stores data on local disk and exports it to Kinesis Data Streams in batches, using temporary credentials from the token exchange role. It retries after outages, so data waits on the gateway rather than being lost."),
        ("Do I need IoT SiteWise to use Greengrass?",
         "No. Greengrass is a general edge runtime. SiteWise Edge is one set of components that runs on it and is useful for reading industrial machines; you can use its collectors and still skip SiteWise cloud storage."),
        ("How much does Greengrass cost?",
         "A small monthly fee per gateway that connects to AWS, with the first three free for a year. The bigger costs are what the gateway sends to, such as Kinesis, IoT Core messages and CloudWatch logs."),
    ],
    "sources": [
        ("AWS docs: What is AWS IoT Greengrass (v1 end of support notice)", "https://docs.aws.amazon.com/greengrass/v2/developerguide/what-is-iot-greengrass.html"),
        ("AWS docs: Greengrass nucleus lite", "https://docs.aws.amazon.com/greengrass/v2/developerguide/greengrass-nucleus-lite-component.html"),
        ("AWS docs: Stream manager component", "https://docs.aws.amazon.com/greengrass/v2/developerguide/stream-manager-component.html"),
        ("AWS docs: Greengrass V2 endpoints and quotas", "https://docs.aws.amazon.com/general/latest/gr/greengrassv2.html"),
        ("AWS IoT Greengrass pricing", "https://aws.amazon.com/greengrass/pricing/"),
        ("AWS docs: Greengrass feature compatibility", "https://docs.aws.amazon.com/greengrass/v2/developerguide/operating-system-feature-support-matrix.html"),
    ],
    "related": [
        ("Streaming on AWS and Databricks", "/learn/streaming/"),
        ("AWS IoT SiteWise and SiteWise Edge", "svc:iot-sitewise"),
        ("AWS IoT Core", "svc:iot-core"),
        ("Amazon Kinesis Data Streams", "svc:kinesis-data-streams"),
        ("Data platform on AWS and Databricks", "/learn/data-platform-architecture/aws-databricks/"),
    ],
}
