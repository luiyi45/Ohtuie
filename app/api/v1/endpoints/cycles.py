from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import timedelta

from app import crud, models, schemas
from app.api import deps

router = APIRouter()

@router.get("", response_model=List[schemas.Cycle])
@router.get("/", response_model=List[schemas.Cycle], include_in_schema=False)
async def read_cycles(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve cycles.
    """
    if current_user.role == "admin":
        cycles = await crud.cycle.get_multi(db, skip=skip, limit=limit) # Admin sees all? Maybe logic needs refinement
    else:
        cycles = await crud.cycle.get_multi_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return cycles

@router.post("", response_model=schemas.Cycle)
@router.post("/", response_model=schemas.Cycle, include_in_schema=False)
async def create_cycle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    cycle_in: schemas.CycleCreate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new cycle.
    """
    cycle = await crud.cycle.create_with_owner(db=db, obj_in=cycle_in, user_id=current_user.id)
    return cycle

@router.put("/{id}", response_model=schemas.Cycle)
async def update_cycle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: UUID,
    cycle_in: schemas.CycleUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update a cycle.
    """
    cycle = await crud.cycle.get(db=db, id=id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    if current_user.role != "admin" and cycle.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    cycle = await crud.cycle.update(db=db, db_obj=cycle, obj_in=cycle_in)
    return cycle

@router.post("/delete-batch", response_model=Any)
async def delete_cycles_batch(
    *,
    db: AsyncSession = Depends(deps.get_db),
    request_data: schemas.DeleteBatchRequest,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete multiple cycles.
    """
    ids = request_data.ids
    # Verify ownership for all IDs
    result = await db.execute(
        select(models.Cycle).filter(models.Cycle.id.in_(ids), models.Cycle.user_id == current_user.id)
    )
    valid_cycles = result.scalars().all()
    valid_ids = [c.id for c in valid_cycles]
    
    if not valid_ids:
        return {"message": "No valid cycles found to delete"}
        
    count = await crud.cycle.remove_batch(db=db, ids=valid_ids)
    return {"message": f"Successfully deleted {count} cycle records"}

@router.delete("/clear-history", response_model=Any)
async def clear_cycle_history(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Clear all cycle history for the current user.
    """
    count = await crud.cycle.remove_all_by_user(db=db, user_id=current_user.id)
    return {"message": f"Successfully deleted {count} cycle records"}

@router.delete("/{id}", response_model=schemas.Cycle)
async def delete_cycle(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: UUID,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a cycle.
    """
    cycle = await crud.cycle.get(db=db, id=id)
    if not cycle:
        raise HTTPException(status_code=404, detail="Cycle not found")
    if current_user.role != "admin" and cycle.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    cycle = await crud.cycle.remove(db=db, id=id)
    return cycle

@router.get("/prediction", response_model=Any)
async def get_prediction(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get predictions for period, ovulation, and fertile window.
    """
    # Logic for prediction
    # 1. Get all cycles to calculate average duration
    cycles = await crud.cycle.get_multi_by_user(db=db, user_id=current_user.id, limit=100)
    if not cycles:
         return {"message": "Not enough data for predictions"}
    
    # Calculate average cycle duration if we have at least 2 cycles
    avg_cycle_days = current_user.cycle_duration or 28
    if len(cycles) >= 2:
        durations = []
        for i in range(len(cycles) - 1):
            # Cycles are ordered by start_date desc, so cycles[i] is newer than cycles[i+1]
            diff = (cycles[i].start_date - cycles[i+1].start_date).days
            if 15 < diff < 45: # Sanity check for cycle length
                durations.append(diff)
        
        if durations:
            avg_cycle_days = sum(durations) // len(durations)

    last_cycle = cycles[0] # Most recent cycle
    
    next_period_start = last_cycle.start_date + timedelta(days=avg_cycle_days)
    ovulation_date = next_period_start - timedelta(days=14)
    # Fertile window is usually 5 days before ovulation plus the day of ovulation
    fertile_window_start = ovulation_date - timedelta(days=5)
    fertile_window_end = ovulation_date + timedelta(days=1)
    
    return {
        "last_period_start": last_cycle.start_date,
        "next_period_start": next_period_start,
        "ovulation_date": ovulation_date,
        "period_duration": current_user.period_duration or 5,
        "avg_cycle_duration": avg_cycle_days,
        "fertile_window": {
            "start": fertile_window_start,
            "end": fertile_window_end
        }
    }

@router.get("/analysis", response_model=Any)
async def get_cycle_analysis(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get detailed cycle analysis, including regularity, symptoms, and correlations.
    """
    from datetime import date
    import statistics
    from collections import Counter

    # 1. Fetch all cycles
    cycles = await crud.cycle.get_multi_by_user(db=db, user_id=current_user.id, limit=1000)
    
    avg_cycle_length = current_user.cycle_duration or 28
    regularity_score = 100
    last_cycle_length = 0
    anomalies = []

    if len(cycles) >= 2:
        durations = []
        for i in range(len(cycles) - 1):
            diff = (cycles[i].start_date - cycles[i+1].start_date).days
            if 15 < diff < 50:
                durations.append(diff)
        
        if durations:
            avg_cycle_length = sum(durations) / len(durations)
            if len(durations) >= 2:
                std_dev = statistics.stdev(durations)
                # Regularity score: 100 - (std_dev * 5) capped at 0-100
                regularity_score = max(0, min(100, int(100 - (std_dev * 5))))
            
            last_cycle_length = durations[0]

    # Check for current cycle delay
    if cycles:
        days_since_last_start = (date.today() - cycles[0].start_date).days
        if days_since_last_start > (avg_cycle_length + 5):
            anomalies.append({
                "title": "Retraso detectado",
                "description": f"Tu ciclo actual lleva {days_since_last_start} días, lo cual es {int(days_since_last_start - avg_cycle_length)} días más que tu promedio habitual.",
                "severity": "warning"
            })
    
    if not anomalies and last_cycle_length > (avg_cycle_length + 5):
        anomalies.append({
            "title": "Ciclo anterior largo",
            "description": f"Tu último ciclo fue de {last_cycle_length} días, significativamente más largo que tu promedio.",
            "severity": "info"
        })

    # 2. Fetch daily logs for symptoms and moods
    logs = await crud.daily_log.get_multi_by_user(db=db, user_id=current_user.id, limit=1000)
    
    symptom_counts = Counter()
    mood_counts = Counter()
    correlations = []
    
    # Track pairs for "Detective" logic
    pair_counts = Counter()

    symptom_map = {
        "cramps": "Cólicos",
        "bloating": "Hinchazón",
        "headache": "Dolor de cabeza",
        "acne": "Acné",
        "tender_breasts": "Sensibilidad mamaria",
        "fatigue": "Fatiga",
        "backache": "Dolor de espalda",
        "nausea": "Náuseas",
        "insomnia": "Insomnio"
    }
    
    mood_map = {
        "happy": "Feliz",
        "sad": "Triste",
        "irritable": "Irritable",
        "anxious": "Ansiosa",
        "calm": "Tranquila",
        "energetic": "Enérgica",
        "sensitive": "Sensible",
        "low_energy": "Cansada"
    }

    icon_map = {
        "Cólicos": "lib/assets/image/colicos.png",
        "Hinchazón": "lib/assets/image/hinchazon.png",
        "Fatiga": "lib/assets/image/fatiga.png",
        "Dolor de cabeza": "lib/assets/image/fatiga.png", # Fallback icons
        "Sensibilidad mamaria": "lib/assets/image/colicos.png",
    }

    for log in logs:
        symptoms = log.symptoms or []
        moods = log.moods or []
        
        for s in symptoms:
            label = symptom_map.get(s, s.capitalize())
            symptom_counts[label] += 1
            for m in moods:
                m_label = mood_map.get(m, m.capitalize())
                pair_counts[(label, m_label)] += 1
        
        for m in moods:
            label = mood_map.get(m, m.capitalize())
            mood_counts[label] += 1

    # Format symptoms summary
    symptoms_summary = [
        {
            "label": k, 
            "count": v, 
            "icon": icon_map.get(k, "lib/assets/image/colicos.png"),
            "trend": "stable"
        } 
        for k, v in symptom_counts.most_common(5)
    ]

    # Format emotions summary
    total_moods = sum(mood_counts.values()) or 1
    emotions_summary = [
        {"label": k, "percentage": int((v / total_moods) * 100)}
        for k, v in mood_counts.most_common(5)
    ]

    # Generate Detective Correlation
    if pair_counts:
        (top_symptom, top_mood), count = pair_counts.most_common(1)[0]
        if count >= 2: # Only show if it happened more than once
            correlations.append({
                "pattern": f"{top_symptom} + {top_mood}",
                "insight": f"Notamos que cuando tienes {top_symptom.lower()}, tu estado de ánimo suele ser '{top_mood}'.",
                "recommendation": "Te recomendamos llevar un registro detallado en estos días para identificar qué actividades te ayudan a sentirte mejor."
            })

    # Default if no correlations found
    if not correlations:
        correlations.append({
            "pattern": "Sin patrones detectados",
            "insight": "Aún estamos recopilando datos para encontrar patrones en tu ciclo.",
            "recommendation": "Registra tus síntomas y estados de ánimo diariamente para obtener mejores análisis."
        })

    return {
        "avg_cycle_length": int(avg_cycle_length),
        "last_cycle_length": last_cycle_length,
        "regularity_score": regularity_score,
        "anomalies": anomalies,
        "correlations": correlations,
        "symptoms_summary": symptoms_summary,
        "emotions_summary": emotions_summary
    }
