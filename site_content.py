from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class LinkItem:
    label: str
    url: str


@dataclass(slots=True)
class Profile:
    name: str
    name_zh: str = ""
    title_lines: list[str] = field(default_factory=list)
    bio_paragraphs: list[str] = field(default_factory=list)
    links: list[LinkItem] = field(default_factory=list)
    portrait_path: str = "assets/images/portrait-placeholder.svg"


@dataclass(slots=True)
class NewsItem:
    date_label: str
    text: str
    is_new: bool = False


@dataclass(slots=True)
class Author:
    name: str
    url: str | None = None
    highlight: bool = False
    suffixes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AuthorDirectoryEntry:
    display_name: str
    url: str | None = None


@dataclass(slots=True)
class AuthorRef:
    id: str
    highlight: bool = False
    suffixes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PublicationLink:
    label: str
    url: str | None = None


@dataclass(slots=True)
class Publication:
    title: str
    authors: list[str | AuthorRef]
    venue: str
    year: int
    image_path: str
    links: list[PublicationLink] = field(default_factory=list)
    summary: str | None = None


@dataclass(slots=True)
class ExperienceItem:
    institution: str
    role: str
    period: str
    details: list[str] = field(default_factory=list)
    logo_path: str = "assets/images/experience-placeholder.svg"


@dataclass(slots=True)
class AwardItem:
    text: str


@dataclass(slots=True)
class ServiceItem:
    text: str


@dataclass(slots=True)
class SiteData:
    page_title: str
    profile: Profile
    author_directory: dict[str, AuthorDirectoryEntry] = field(default_factory=dict)
    news: list[NewsItem] = field(default_factory=list)
    publications: list[Publication] = field(default_factory=list)
    experiences: list[ExperienceItem] = field(default_factory=list)
    services: list[ServiceItem] = field(default_factory=list)
    awards: list[AwardItem] = field(default_factory=list)
    publication_note: str | None = None
    footer_note: str | None = None


def author_ref(
    author_id: str,
    *,
    highlight: bool = False,
    suffixes: list[str] | None = None,
) -> AuthorRef:
    return AuthorRef(
        id=author_id,
        highlight=highlight,
        suffixes=[] if suffixes is None else suffixes,
    )


SITE = SiteData(
    page_title="Su Jiayi | 苏佳奕",
    profile=Profile(
        name="Su Jiayi",
        name_zh="苏佳奕",
        title_lines=[
            'Hiii, there!',
            (
                'I am currently a <span id="phd-year" data-start-year="2026" data-start-month="9">first-year</span> Ph.D. student at '
                '<a href="http://www.ia.cas.cn/">CASIA</a>, '
                '<a href="https://www.galbot.com/">Galbot</a>, and '
                '<a href="https://pku-epic.github.io/">EPIC Lab</a> (2026-present). '
                'Before that, I received my B.Sc. degree in Computer Science and Technology from '
                '<a href="https://www.xmu.edu.my/">Xiamen University</a> (2022-2026). '
                'I am currently an intern at <a href="https://www.galbot.com/">Galbot</a>, under the supervision of '
                '<a href="https://hughw19.github.io/">Prof. He Wang</a> '
                'and <a href="https://scholar.google.com/citations?user=X7M0I8kAAAAJ&hl=en">Prof. Zhizheng Zhang</a>.'
            )
        ],
        bio_paragraphs=[
            (
                "I am interested in embodied AI, VLA for manipulation, world models, and video models for robotics."
            ),
            (
                'I am lucky to work closely with <a href="https://miyandoris.github.io/">Mi Yan</a>, '
                '<a href="https://jiangranlv.github.io/">Jiangran Lyu</a>, and '
                '<a href="https://shengliangd.github.io/about/">Shengliang Deng</a>.'
            )
        ],
        links=[
            LinkItem(label="Email", url="mailto:CST2209162@xmu.edu.my"),
            LinkItem(label="Github", url="https://github.com/ShuYuMo2003"),
            LinkItem(label="X", url="https://x.com/JiaYiSu8"),
            LinkItem(label="OI Blog", url="oi-blog/index.html"),
            LinkItem(label="Luogu", url="https://www.luogu.com.cn/user/44615"),
        ],
        portrait_path="assets/images/me.jpg",
    ),
    news=[
        # NewsItem(
        #     date_label="2026/03",
        #     text="Built this academic website generator based on a cleaned version of the reference layout.",
        #     is_new=True,
        # ),
    ],
    publications=[
        # Plain strings are author ids; use author_ref(...) when you need highlight/suffix. 
        # suffixes: *: joint first author; &dagger; project lead; &#9993; corresponding author(s)
        Publication(
            title="GPT 6 Astra as an Embodied Policy",
            authors=[
                author_ref("Jiayi Su", highlight=True, suffixes=["*"]),
                author_ref("Yixin Zheng", suffixes=["*"]),
                author_ref("Mi Yan"),
                author_ref("Li Yi"),
                author_ref("Zhizheng Zhang", suffixes=["&#9993;"]),
                author_ref("He Wang", suffixes=["&#9993;"]),
            ],
            venue="Technical Report",
            year=2026,
            image_path="assets/images/papers/astra-front-page.png",
            links=[
                PublicationLink(
                    label="project page",
                    url="https://anonymous-report-421.github.io/public-website/?view=1",
                ),
                PublicationLink(
                    label="code",
                    url="https://github.com/anonymous-report-421/eval-of-gpt-6-astra-as-policy",
                ),
                PublicationLink(
                    label="具身智能之心",
                    url="https://mp.weixin.qq.com/s/e8Tx4EL9qDDZNGcIwNmV5w",
                ),
                PublicationLink(
                    label="腾讯科技",
                    url="https://mp.weixin.qq.com/s/KPIVOsmAV3FAHmyo6do3dQ",
                ),
                PublicationLink(
                    label="智能纪元AGI",
                    url="https://mp.weixin.qq.com/s/TaGZRbPEFmw5VBmy26bq8g",
                ),
                PublicationLink(
                    label="human five",
                    url="https://mp.weixin.qq.com/s/cc6OYHSUtCI7qPZl46cBgA",
                ),
            ],
            summary=(
                "A technical report comparing direct GPT 6 Astra control with a hybrid "
                "π0.5 + GPT 6 Astra policy for zero-shot bimanual manipulation. On the "
                "selected RoboDojo tasks, the hybrid policy reaches 48% success and a "
                "62.60 mean score, compared with 26% and 37.81 for direct control."
            ),
        ),
        Publication(
            title="ZETA: A Controlled Study of Zero-Shot Cross-Embodiment VLA Transfer for Tabletop Manipulation",
            authors=[
                author_ref("Mi Yan", suffixes=["*"]),
                author_ref("Wenhao Zhang", suffixes=["*"]),
                author_ref("Zhiqi Zhang", suffixes=["*"]),
                author_ref("Yu Peng", suffixes=["*"]),
                author_ref("Tangxinyu Wang", suffixes=["*"]),
                "Lingfei Zhai",
                author_ref("Jiayi Su", highlight=True),
                author_ref("Shengliang Deng"),
                "Lin Peng",
                "Yaowei Liu",
                "Yuxing Chen",
                "Zhiyuan Wei",
                "Jilong Wang",
                "Jiayi Chen",
                author_ref("Jiangran Lyu"),
                author_ref("Zhizheng Zhang", suffixes=["&#9993;"]),
                author_ref("He Wang", suffixes=["&#9993;"]),
            ],
            venue="CoRL",
            year=2026,
            image_path="assets/images/papers/zeta.jpg",
            links=[
                PublicationLink(label="project page", url="https://theone2006.github.io/ZETA-Web/"),
                PublicationLink(label="paper", url="https://arxiv.org/abs/2609.02546"),
                PublicationLink(label="code", url="https://github.com/MiYanDoris/ZETA"),
            ],
            summary="ZETA presents a controlled study of zero-shot cross-embodiment transfer for vision-language-action models in tabletop manipulation.",
        ),
        Publication(
            title="StereoVLA: Enhancing Vision-Language-Action Models with Stereo Vision",
            authors=[
                author_ref("Shengliang Deng", suffixes=["*"]),
                author_ref("Mi Yan", suffixes=["*"]),
                author_ref("Yixin Zheng", suffixes=["*"]),
                author_ref("Jiayi Su", highlight=True),
                "Wenhao Zhang",
                "Xiaoguang Zhao",
                "Heming Cui",
                author_ref("Zhizheng Zhang", suffixes=["&#9993;"]),
                author_ref("He Wang", suffixes=["&#9993;"]),
            ],
            venue="RSS",
            year=2026,
            image_path="assets/images/papers/stereovla.jpg",
            links=[
                PublicationLink(label="arXiv", url="https://arxiv.org/abs/2512.21970"),
                PublicationLink(label="code", url="https://github.com/shengliangd/StereoVLA"),
                PublicationLink(label="checkpoint", url="https://huggingface.co/shengliangd/StereoVLA"),
            ],
            summary="StereoVLA is powered by stereo vision and supports zero-shot deployment with high tolerance to camera pose variations."
        ),
        Publication(
            title="ArtFormer: Controllable Generation of Diverse 3D Articulated Objects",
            authors=[
                author_ref("Jiayi Su", highlight=True, suffixes=["*", "&#9993;"]),
                author_ref("Youhe Feng", suffixes=["*"]),
                "Zheng Li",
                "Jinhua Song",
                "Yangfan He",
                "Botao Ren",
                author_ref("Botian Xu", suffixes=["&#9993;"]),
            ],
            venue="CVPR (top 15%)",
            year=2025,
            image_path="assets/images/papers/artformer.gif",
            links=[
                PublicationLink(label="arXiv", url="https://arxiv.org/abs/2412.07237"),
                PublicationLink(label="code", url="https://github.com/ShuYuMo2003/ArtFormer"),
            ],
            summary="ArtFormer introduces a novel transformer-based framework that generates diverse, high-quality 3D articulated objects from text description or single image."
        ),
        # Publication(
        #     title="Robust 3D Human Pose Estimation with Unsynchronized Cross-View Fusion",
        #     authors=[
        #         "Liu Yuhang",
        #         "Huibin Kang",
        #         "Hengan Liu",
        #         author_ref("Jiayi Su", highlight=True),
        #         "Keng-Lun Chang",
        #         "Jiaqing Lyu",
        #         "Bo Wan",
        #     ],
        #     venue="ICME Workshop",
        #     year=2025,
        #     image_path="assets/images/papers/human_pose_estm.jpg",
        #     links=[
        #         PublicationLink(label="paper", url="https://www.computer.org/csdl/proceedings-article/icmew/2025/11152122/29TBBn6CN8Y"),
        #     ]
        # ),
    ],
    experiences=[
        ExperienceItem(
            institution="University of Chinese Academy of Sciences",
            role="Ph.D. Student at CASIA (Institute of Automation)",
            period="2026.09 - present",
            logo_path="assets/images/CAS-logo.png",
        ),
        ExperienceItem(
            institution="Galbot",
            role="Large Embodied Model Researcher",
            period="2025.08 - present",
            details=["VLA & Simulation Pipe Engineer"],
            logo_path="assets/images/galbot.jpg",
        ),
        ExperienceItem(
            institution="Shanghai Jiao Tong University",
            role="Research Assistant",
            period="2025.02 - 2025.05",
            details=[
                "Research focus: DiT inference optimization",
            ],
            logo_path="assets/images/Sjtu-logo-standard-red.png",
        ),
        ExperienceItem(
            institution="Xiamen University",
            role="B.Sc. in Computer Science and Technology",
            period="2022.09 - 2026",
            details=[
                "Rank: 1/71; Grade: 97.0 / 100 (3.88 / 4.00)",
            ],
            logo_path="assets/images/Xiamen_University_logo.svg.png",
        ),
    ],
    services=[
        ServiceItem(text="CVPR 2026 Reviewer"),
        ServiceItem(text="ICME 2025 Reviewer"),
    ],
    awards=[
        AwardItem(text="2022-2025 First-Class Scholarship (Xiamen University)"),
        AwardItem(text='2021 <a href="https://www.noi.cn/">National Olympiad in Informatics (NOI)</a>, Winter Camp, Silver Medal'),
        AwardItem(text='2021 <a href="https://www.noi.cn/">National Olympiad in Informatics (NOI)</a>, Bronze Medal'),
        AwardItem(text='2020-2022 <a href="https://zh.wikipedia.org/wiki/%E5%85%A8%E5%9B%BD%E9%9D%92%E5%B0%91%E5%B9%B4%E4%BF%A1%E6%81%AF%E5%AD%A6%E5%A5%A5%E6%9E%97%E5%8C%B9%E5%85%8B%E8%81%94%E8%B5%9B">National Olympiad in Informatics in Provinces (NOIP)</a> First Prize, Rank 10'),
    ],
    publication_note="*: joint first author; &dagger; project lead; &#9993; corresponding author(s)",
    footer_note='Style adapted from <a style="font-size: x-small" href="https://jonbarron.info/">Jon Barron</a>.',
    # Use display names as ids by default; use a custom id only when names collide.
    author_directory={
        "Jiayi Su": AuthorDirectoryEntry(
            display_name="Jiayi Su",
            url="https://shuyumo2003.github.io/"
        ),
        "Youhe Feng": AuthorDirectoryEntry(
            display_name="Youhe Feng",
            url="https://scholar.google.com/citations?user=qb81QakAAAAJ&hl=en",
        ),
        "Botao Ren": AuthorDirectoryEntry(
            display_name="Botao Ren",
            url="https://scholar.google.com/citations?user=BTaRU00AAAAJ&hl=en",
        ),
        "Botian Xu": AuthorDirectoryEntry(
            display_name="Botian Xu",
            url="https://btx0424.github.io/",
        ),
        "Shengliang Deng": AuthorDirectoryEntry(
            display_name="Shengliang Deng",
            url="https://shengliangd.github.io/about/",
        ),
        "Mi Yan": AuthorDirectoryEntry(
            display_name="Mi Yan",
            url="https://miyandoris.github.io/",
        ),
        "Tangxinyu Wang": AuthorDirectoryEntry(
            display_name="Tangxinyu Wang",
            url="https://theone2006.github.io/",
        ),
        "Jiangran Lyu": AuthorDirectoryEntry(
            display_name="Jiangran Lyu",
            url="https://jiangranlv.github.io/",
        ),
        "Wenhao Zhang": AuthorDirectoryEntry(
            display_name="Wenhao Zhang",
            url="https://openreview.net/profile?id=~Wenhao_Zhang28",
        ),
        "Zhiqi Zhang": AuthorDirectoryEntry(
            display_name="Zhiqi Zhang",
            url="https://openreview.net/profile?id=~Zhiqi_Zhang3",
        ),
        "Yu Peng": AuthorDirectoryEntry(
            display_name="Yu Peng",
            url="https://openreview.net/profile?id=~Yu_Peng4",
        ),
        "Lingfei Zhai": AuthorDirectoryEntry(
            display_name="Lingfei Zhai",
            url="https://openreview.net/profile?id=~Lingfei_Zhai1",
        ),
        "Lin Peng": AuthorDirectoryEntry(
            display_name="Lin Peng",
            url="https://openreview.net/profile?id=~Lin_Peng4",
        ),
        "Yaowei Liu": AuthorDirectoryEntry(
            display_name="Yaowei Liu",
            url="https://openreview.net/profile?id=~Yaowei_Liu3",
        ),
        "Yuxing Chen": AuthorDirectoryEntry(
            display_name="Yuxing Chen",
            url="https://chen01yx.github.io/",
        ),
        "Zhiyuan Wei": AuthorDirectoryEntry(
            display_name="Zhiyuan Wei",
            url="https://openreview.net/profile?id=~Zhiyuan_Wei4",
        ),
        "Jilong Wang": AuthorDirectoryEntry(
            display_name="Jilong Wang",
            url="https://42jaylonw.github.io/",
        ),
        "Jiayi Chen": AuthorDirectoryEntry(
            display_name="Jiayi Chen",
            url="https://jychen18.github.io/",
        ),
        "Yixin Zheng": AuthorDirectoryEntry(
            display_name="Yixin Zheng",
            url="https://steveouo.github.io/",
        ),
        "Li Yi": AuthorDirectoryEntry(
            display_name="Li Yi",
            url="https://ericyi.github.io/",
        ),
        "Zhizheng Zhang": AuthorDirectoryEntry(
            display_name="Zhizheng Zhang",
            url="https://scholar.google.com/citations?user=X7M0I8kAAAAJ&hl=en",
        ),
        "He Wang": AuthorDirectoryEntry(
            display_name="He Wang",
            url="https://hughw19.github.io/",
        ),
        "Heming Cui": AuthorDirectoryEntry(
            display_name="Heming Cui",
            url="https://i.cs.hku.hk/~heming/",
        ),
    },
)
