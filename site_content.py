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
class SiteData:
    page_title: str
    profile: Profile
    author_directory: dict[str, AuthorDirectoryEntry] = field(default_factory=dict)
    news: list[NewsItem] = field(default_factory=list)
    publications: list[Publication] = field(default_factory=list)
    experiences: list[ExperienceItem] = field(default_factory=list)
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
                'I am currently an undergraduate student at '
                '<a href="https://www.xmu.edu.my/">Xiamen U M</a> (2022-2026), '
                'and will begin the joint Ph.D. program of <a href="http://www.ia.cas.cn/">CASIA</a> & '
                '<a href="https://www.baai.ac.cn/">BAAI</a> & '
                '<a href="https://www.galbot.com/">Galbot</a> & '
                '<a href="https://pku-epic.github.io/">EPIC Lab</a> in summer 2026. '
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
                '<a href="https://shengliangd.github.io/about/">Shengliang Deng</a>, '
                'and grateful for their help during the early stage of my internship.'
            )
        ],
        links=[
            LinkItem(label="Email", url="mailto:CST2209162@xmu.edu.my"),
            LinkItem(label="Github", url="https://github.com/ShuYuMo2003"),
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
            venue="preprint",
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
        Publication(
            title="Robust 3D Human Pose Estimation with Unsynchronized Cross-View Fusion",
            authors=[
                "Liu Yuhang",
                "Huibin Kang",
                "Hengan Liu",
                author_ref("Jiayi Su", highlight=True),
                "Keng-Lun Chang",
                "Jiaqing Lyu",
                "Bo Wan",
            ],
            venue="ICME Workshop",
            year=2025,
            image_path="assets/images/papers/human_pose_estm.jpg",
            links=[
                PublicationLink(label="paper", url="https://www.computer.org/csdl/proceedings-article/icmew/2025/11152122/29TBBn6CN8Y"),
            ]
        ),
    ],
    experiences=[
        ExperienceItem(
            institution="Xiamen University (Malaysia)",
            role="Undergraduate Student in CST",
            period="2022.09 - present",
            details=[
                "Rank: 1/71; Grade: 97.0 / 100 (3.88 / 4.00)",
            ],
            logo_path="assets/images/Xiamen_University_logo.svg.png",
        ),
        ExperienceItem(
            institution="Galbot",
            role="Embodied Large Model Researcher",
            period="2025.08 - present",
            details=[],
            logo_path="assets/images/galbot.jpg",
        ),
    ],
    awards=[
        # AwardItem(text="2025 Outstanding Student Award"),
        # AwardItem(text="2024 Department Fellowship"),
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
