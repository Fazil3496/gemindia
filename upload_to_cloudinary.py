import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

DOWNLOADS = r"C:\Users\fazzi\Downloads"

# Your 70 gemindia images mapped to place IDs
images = [
    ("place_1", "Agumbe_Sunset_Point_Main.jpg"),
    ("place_2", "Yana caves.jpg"),
    ("place_3", "Shettihalli_Rosary_Church_in_night_sky.jpg"),
    ("place_4", "st mary copy right free.jpg"),
    ("place_5", "rahul-WQAzQyRo2Fc-unsplash.jpg"),
    ("place_6", "sujit-bangarshettar-JCjfauZPPg8-unsplash.jpg"),
    ("place_7", "Devarayanadurga_hills.jpg"),
    ("place_8", "Sakleshpur_P1010194.JPG"),
    ("place_9", "Coorg_(Kodagu),_Karnataka,_India_(2022)_03.jpg"),
    ("place_10", "The_Kapila_river_in_Nanjangud.jpg"),
    ("place_11", "Relief_of_Jain_Tirthankara_Parshvanath_in_the_Badami_cave_temple_no.4.jpg"),
    ("place_12", "Krishna_Pushkarani_-_Hampi_Ruins.jpg"),
    ("place_13", "Jog_falls_shivamogga.jpg"),
    ("place_14", "PXL_20260103_054657562.MP_Paradise_beach_gokarna_Paradise_Beach_Trail,_Gokarna,_Karnatak..."),
    ("place_15", "Nandi_at_Nandi_Hills-1.jpg"),
    ("place_16", "Baba_Budangiri,_Chikmagalur_(2024)_80.jpg"),
    ("place_17", "Halebidu_-_Karnataka.jpg"),
    ("place_18", "Shola_Grasslands_and_forests_in_the_Kudremukh_National_Park,_Western_Ghats,_Karnataka.jpg"),
    ("place_19", "Mysore_Palace_Morning.jpg"),
    ("place_20", "Bidar_fort_complex_from_Solah_Khambha_Masjid.jpg"),
    ("place_21", "Aihole_group_of_monuments_-_hamvrvb102k22_(21).jpg"),
    ("place_22", "Pattadakal_Temple_Complex,_Bagalkot_district.jpg"),
    ("place_23", "Murudeshwar_2.jpg"),
    ("place_24", "640px-Cauvery_Kaveri_River_Karnataka_India_(2).jpg"),
    ("place_25", "Skandagiri_hills_top_in_Chikkaballapur_district_-1.jpg"),
    ("place_26", "Ramanagara_Hills_(10306067976).jpg"),
    ("place_27", "Shivanasamudra_Falls,_Karnataka,_India.jpg"),
    ("place_28", "Nagarhole_National_Park,_Kodagu_6895.JPG"),
    ("place_29", "Kollur_Mookambika_Temple_20080123.JPG"),
    ("place_30", "Kodachadri,_Shivamogga,_Karnataka,_India_7417_(14369705651).jpg"),
    ("place_31", "640px-Kali_River_Karwar_Karnataka_India.jpg"),
    ("place_32", "Bisle_ghat,_Subramanya-Sakleshpur_road,_01.jpg"),
    ("place_33", "Islands_Cauvery_Ranganathittu_Karnataka_Feb24_R16_07728.jpg"),
    ("place_34", "A_group_of_dholes_in_Bandipur_national_park.jpg"),
    ("place_35", "Chitradurga_fort_Image_(10),_Karnataka,_India.jpg"),
    ("place_36", "The_Tungabhadra_Dam_04.jpg"),
    ("place_37", "Hogenakkal_view.jpg"),
    ("place_38", "Anthargange_(23639166299).jpg"),
    ("place_39", "Madhugiri_Fort_top.jpg"),
    ("place_40", "Savandurga_view.jpg"),
    ("place_41", "Bylakuppe._Mysore_(3).jpg"),
    ("place_42", "Tunga_River_Steps,_Sringeri,_2019.jpg"),
    ("place_43", "Kemmanagundi_View.jpg"),
    ("place_44", "Brhills_kkatte.jpg"),
    ("place_45", "Netrani_Island_Arial_View.jpg"),
    ("place_46", "Bijapur_railway_station_at_Vijayapura_in_Karnataka_02.jpg"),
    ("place_47", "View_of_Akkana_Basadi_from_northeastern_side_at_Shravanabelagola.jpg"),
    ("place_48", "Maravanthe_Beach_4.jpg"),
    ("place_49", "Shri_Udupi_Krishna_Temple's_Madhwa_Sarovara_view.jpg"),
    ("place_50", "Milagres_Charch,_Hampanakatte,_Mangaluru_2.jpg"),
    ("place_51", "Kukke_Subramanya_Temple_5.jpg"),
    ("place_52", "Kumara_Parvatha_cliff.JPG"),
    ("place_53", "Honnemaradu_4.JPG"),
    ("place_54", "Talakaveri_valley_shola.jpg"),
    ("place_55", "Unchalli_falls_SIRSI.png"),
    ("place_56", "Tusker_at_Dubare_Elephant_Camp_Kodagu.jpg"),
    ("place_57", "Talakad_(7727190192).jpg"),
    ("place_58", "640px-Melukote,_Karnataka_IMG_8291_(43844704485).jpg"),
    ("place_59", "Reservoir_with_Bhadra_Wildlife_Sanctuary_in_Chikmagalur_District_of_Karnataka_India_02.jpg"),
    ("place_60", "Skandagiri_Trek_Forest_Reception_Counter_3.jpg"),
    ("place_61", "Backwater_subadult_tiger_with_mum_(51341064164).jpg"),
    ("place_62", "Sri_Biligiri_Ranganathaswamy.jpg"),
    ("place_63", "640px-Gulbarga_fort_2.jpg"),
    ("place_64", "Kodi_beach_2.jpg"),
    ("place_65", "Channapatna_toys53.jpg"),
    ("place_67", "Panoramic_view_from_Avalabetta.jpg"),
    ("place_68", "Enroute_Galibore_Fishing_Camp_-_cauvery_river_-_tree.jpg"),
    ("place_69", "Coffee_plantation_of_Chikkamagaluru_2.jpg"),
    ("place_70", "Images_from_Canacona.jpg"),
]

print("🚀 Starting upload to Cloudinary from Downloads folder...")
print("="*50)

results = {}

for public_id, filename in images:
    filepath = os.path.join(DOWNLOADS, filename)
    if os.path.exists(filepath):
        try:
            response = cloudinary.uploader.upload(
                filepath,
                public_id=public_id,
                folder="gemindia",
                overwrite=True
            )
            url = response['secure_url']
            results[public_id] = url
            print(f"✅ {public_id} → {url}")
        except Exception as e:
            print(f"❌ Failed {public_id}: {e}")
    else:
        print(f"⚠️  File not found: {filename}")

print("="*50)
print(f"✅ Done! {len(results)}/70 images uploaded!")